from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.code_index.index import CodeIndex

if __name__ == "__main__":
    reader = RepoReader(".")
    index = CodeIndex(reader)

    # Build index
    index.build_index()

    # Test search
    print("\n🔍 Testing semantic search:")
    query = "function that reads files"
    results = index.search(query, top_k=3)

    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    File: {result['file']}")
        print(f"    Lines:  {result['lines']}")
        print(f"    Type: {result['type']}")
        if result["name"]:
            print(f"    Name: {result['name']}")
        print(f"    Code preview: {result['code'][:100]}...")
