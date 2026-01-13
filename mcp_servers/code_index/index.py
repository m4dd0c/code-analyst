import ast
import os
from typing import List, Dict, Tuple
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
            model="gemini-embedding-1.0",
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

    def _chunk_by_function(self, file_data) -> List[Document]:
        """Split Python files by function/class (semantic chunking)"""
        chunks = []

        try:
            tree = ast.parse(file_data.content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    start_line = node.lineno
                    end_line = node.end_lineno or start_line

                    # extract code chunk
                    code_lines = file_data.lines[start_line - 1 : end_line]
                    code_chunk = "".join(code_lines)

                    chunks.append(
                        Document(
                            page_content=code_chunk,
                            metadata={
                                "file": file_data.path,
                                "lines": f"{start_line}-{end_line}",
                                "type": "function"
                                if isinstance(node, ast.FunctionDef)
                                else "class",
                                "name": node.name,
                                "language": "python",
                            },
                        )
                    )
        except SyntaxError:
            # If AST fails, fall back to line chunking
            return self._chunk_by_lines(file_data)

        return chunks

    def _chunk_by_lines(self, file_data, chunk_size: int = 50) -> List[Document]:
        """Chunk non-python or unparseable files by line count"""
        chunks = []
        lines = file_data.line_count

        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i : i + chunk_size]
            code_chunk = "".join(chunk_lines)

            chunks.append(
                Document(
                    page_content=code_chunk,
                    metadata={
                        "file": file_data.path,
                        "lines": f"{i + 1}-{i + len(chunk_lines)}",
                        "type": "chunk",
                        "language": file_data.extension[1:]
                        if file_data.extension
                        else "unknown",
                    },
                )
            )

        return chunks

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search for relevant code

        Returns:
            List of dicts with code, file, lines, and metadata
        """
        if not self._indexed:
            self.build_index()

        if self.vectorstore is None:
            raise RuntimeError("Code index not built")

        results = self.vectorstore.similarity_search(query, k=top_k)

        return [
            {
                "code": doc.page_content,
                "file": doc.metadata["file"],
                "lines": doc.metadata["lines"],
                "type": doc.metadata["type"],
                "language": doc.metadata.get("language", "unknown"),
                "name": doc.metadata.get("name", ""),
            }
            for doc in results
        ]

    def search_with_scores(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """Search with similarity scores"""
        if not self._indexed:
            self.build_index()

        if self.vectorstore is None:
            raise RuntimeError("Code index not built")

        results = self.vectorstore.similarity_search_with_score(query, k=top_k)

        return [
            (
                {
                    "code": doc.page_content,
                    "file": doc.metadata["file"],
                    "lines": doc.metadata["lines"],
                    "type": doc.metadata["type"],
                    "language": doc.metadata.get("language", "unknown"),
                    "name": doc.metadata.get("name", ""),
                },
                score,
            )
            for doc, score in results
        ]
