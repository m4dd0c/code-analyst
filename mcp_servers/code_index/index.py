import ast
import os
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from mcp_servers.repo_reader.reader import RepoReader
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


class CodeIndex:
    """MCP Server:  Semantic code search with RAG"""

    def __init__(self, repo_reader: RepoReader):
        self.reader = repo_reader
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=SecretStr(api_key) if api_key else None,
        )
        self.vectorstore = None
        self._indexed = False

    def build_index(self):
        """Build vector index from repository code"""
        if self._indexed:
            return self.vectorstore

        print("🔨 Building code index...")
        documents = []

        files = self.reader.walk_repo()
        for file_data in files:
            if file_data.extension == ".py":
                chunks = self._chunk_by_function(file_data)
                documents.extend(chunks)
            else:
                chunks = self._chunk_by_lines(file_data, chunk_size=50)
                documents.extend(chunks)
        print(f"Chunked into {len(documents)} code blocks.")
        print("Generating embeddings (this may take a while)...")

        # build vector store
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self._indexed = True
        print("✅ Code index built Successfully.")
