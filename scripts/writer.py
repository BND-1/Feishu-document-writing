# -*- coding: utf-8 -*-
"""
飞书写入主入口类
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from .auth import FeishuAuth
from .uploader import FeishuImageUploader
from .parser import MarkdownParser
from .doc_writer import FeishuDocWriter


class FeishuWriter:
    """飞书写入主类"""

    def __init__(self):
        load_dotenv()

        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")

        if not app_id or not app_secret:
            raise Exception("请在 .env 文件中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")

        self.auth = FeishuAuth(app_id, app_secret)
        self.uploader = FeishuImageUploader(self.auth)
        self.doc_writer = FeishuDocWriter(self.auth)

    def write_file(
        self,
        md_path: str,
        target: str = "space",
        folder_token: Optional[str] = None,
        wiki_token: Optional[str] = None,
        check_duplicate: bool = True
    ) -> Dict[str, Any]:
        """
        将 MD 文件写入飞书

        Args:
            md_path: MD 文件路径
            target: 目标类型 (space/folder/wiki)
            folder_token: 文件夹 token（target=folder 时必需）
            wiki_token: 知识库 token（target=wiki 时必需）
            check_duplicate: 是否检查重复

        Returns:
            {"success": bool, "document_id": str, "message": str}
        """
        path = Path(md_path)
        if not path.exists():
            return {"success": False, "document_id": None, "message": f"文件不存在: {md_path}"}

        # 读取 MD 文件
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 用文件名作为标题（去掉 .md 扩展名）
        title = path.stem

        # 解析 MD 内容
        parser = MarkdownParser(self.uploader, str(path))
        blocks = parser.parse(content)

        # 检查重复
        existing_doc = None
        if check_duplicate and folder_token:
            docs = self.doc_writer.list_documents_in_folder(folder_token)
            for doc in docs:
                if doc.get("name") == title:
                    existing_doc = doc
                    break

        if existing_doc:
            return {
                "success": False,
                "document_id": None,
                "message": f"duplicate:{existing_doc.get('token')}:{title}",
                "existing_doc": existing_doc
            }

        # 根据目标类型创建文档
        if target == "wiki":
            # 直接在知识库中创建文档
            wiki_space_id = os.getenv("FEISHU_DEFAULT_WIKI_SPACE_ID")
            wiki_node_token = wiki_token or os.getenv("FEISHU_DEFAULT_WIKI_NODE_TOKEN")

            if wiki_node_token and not wiki_space_id:
                wiki_space_id = self.doc_writer.get_wiki_space_id(wiki_node_token)

            if not wiki_space_id:
                return {"success": False, "document_id": None, "message": "未配置知识库 space_id，请在 .env 中配置或通过 --wiki-token 指定"}

            try:
                doc_id, node_token = self.doc_writer.create_wiki_document(
                    title, wiki_space_id, wiki_node_token
                )
            except Exception as e:
                return {"success": False, "document_id": None, "message": f"创建知识库文档失败: {e}"}

            # 写入内容
            if not self.doc_writer.append_blocks(doc_id, doc_id, blocks):
                return {"success": False, "document_id": doc_id, "message": "写入内容失败"}

            return {
                "success": True,
                "document_id": doc_id,
                "node_token": node_token,
                "message": f"成功创建文档: {title}",
                "uploaded_images": parser.uploaded_images
            }
        else:
            # 在云文档中创建
            try:
                doc_id, block_id = self.doc_writer.create_document(
                    title,
                    folder_token if target == "folder" else None
                )
            except Exception as e:
                return {"success": False, "document_id": None, "message": f"创建文档失败: {e}"}

            # 写入内容
            if not self.doc_writer.append_blocks(doc_id, block_id, blocks):
                return {"success": False, "document_id": doc_id, "message": "写入内容失败"}

            return {
                "success": True,
                "document_id": doc_id,
                "message": f"成功创建文档: {title}",
                "uploaded_images": parser.uploaded_images
            }

    def update_document(self, document_id: str, md_path: str) -> Dict[str, Any]:
        """更新已有文档"""
        path = Path(md_path)
        if not path.exists():
            return {"success": False, "message": f"文件不存在: {md_path}"}

        # 读取 MD 文件
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 MD 内容
        parser = MarkdownParser(self.uploader, str(path))
        blocks = parser.parse(content)

        # 清空原内容
        self.doc_writer.delete_document_content(document_id)

        # 写入新内容
        if not self.doc_writer.append_blocks(document_id, document_id, blocks):
            return {"success": False, "message": "更新内容失败"}

        return {
            "success": True,
            "document_id": document_id,
            "message": "文档更新成功",
            "uploaded_images": parser.uploaded_images
        }
