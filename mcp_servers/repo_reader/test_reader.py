from mcp_servers.repo_reader.reader import RepoReader

if __name__ == "__main__":
    # Test on current directory
    reader = RepoReader(".")

    # Get summary
    summary = reader.get_summary()
    print("📊 Repository Summary:")
    print(f"  Files: {summary['total_files']}")
    print(f"  Lines: {summary['total_lines']}")
    print(f"  Extensions: {summary['extensions']}")

    # Get tree
    print("\n🌳 File Tree:")
    print(reader.get_file_tree())

    # Read first file
    files = reader.walk_repo()
    if files:
        first_file = files[0]
        print(f"\n📄 Sample File: {first_file.path}")
        print(f"  Lines: {first_file.line_count}")
        print(f"  Size: {first_file.size} bytes")
