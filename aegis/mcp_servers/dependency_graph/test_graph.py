from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph

if __name__ == "__main__":
    reader = RepoReader(".")
    graph = DependencyGraph(reader)

    # Build graph
    graph.build()

    # Show high fan-in files
    print("\n🎯 Files with highest dependencies (most risky):")
    for file_path, fan_in in graph.get_high_fan_in_files(5):
        print(f"  {file_path}: {fan_in} dependents")

    # Test specific file
    if graph.graph:
        sample_file = list(graph.graph.keys())[0]
        print(f"\n📄 Dependencies for:  {sample_file}")
        print(f"  Imports: {graph.get_dependencies(sample_file)}")
        print(f"  Imported by: {graph.get_dependents(sample_file)}")
