import click
from pathlib import Path
from mcp_servers.repo_reader.reader import RepoReader
from mcp_servers.dependency_graph.graph import DependencyGraph
from mcp_servers.code_index.index import CodeIndex


@click.group()
def cli():
    """Autonomous Code Assistant CLI"""
    pass


@cli.command()
@click.argument("path", default=".")
def analyze(path):
    """Analyze code repository and show summary"""
    click.echo(f"🔍 Analyzing repository: {path}\n")

    try:
        # Init MCP servers
        reader = RepoReader(path)

        # get summary
        summary = reader.get_summary()
        click.echo("📊 Repository Summary:")
        click.echo(f"  Total files: {summary['total_files']}")
        click.echo(f"  Total lines: {summary['total_lines']: ,}")
        click.echo(f"  Total size: {summary['total_size_bytes']:,} bytes")
        click.echo("\n  Files by extension:")
        for ext, count in sorted(
            summary["extensions"].items(), key=lambda x: x[1], reverse=True
        ):
            click.echo(f"    {ext}: {count}")

        # build dependency graph
        click.echo("\n🕸  Building dependency graph...")
        graph = DependencyGraph(reader)
        graph.build()

        # show high risk files
        click.echo("\n⚠️  High-risk files (most dependencies):")
        for file_path, fan_in in graph.get_high_fan_in_files(5):
            click.echo(f"  {file_path}: {fan_in} dependents")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("query")
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--top", default=3, help="Number of result")
def search(query, path, top):
    """Search codebase semantically"""
    click.echo(f"🔍 Searching for: '{query}'\n")
    try:
        reader = RepoReader(path)
        index = CodeIndex(reader)
        index.build_index()

        results = index.search(query, top_k=top)

        for i, result in enumerate(results, 1):
            click.echo(f"Result {i}:")
            click.echo(f"  File: {result['file']}")
            click.echo(f"  Lines: {result['lines']}")
            if result["name"]:
                click.echo(f"  Name: {result['name']}")
            click.echo(f"  Code:\n{result['code'][:200]}...\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("file_path")
@click.option("--path", default=".", help="Path to the code repository")
def impact(file_path, path):
    """Show impact of changing a file"""
    click.echo(f"📊 Impact analysis for: {file_path}\n")

    try:
        reader = RepoReader(path)
        graph = DependencyGraph(reader)
        graph.build()

        dependents = graph.get_dependents(file_path)
        dependencies = graph.get_dependencies(file_path)
        fan_in = graph.get_fan_in(file_path)

        click.echo(f"  Files that depend on this:  {fan_in}")
        if dependents:
            for dep in dependents[:10]:
                click.echo(f"    - {dep}")

        click.echo(f"\n  Files this depends on: {len(dependencies)}")
        if dependencies:
            for dep in dependencies[:10]:
                click.echo(f"    - {dep}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("path", default=".")
def tree(path):
    """Show repository file tree"""
    try:
        reader = RepoReader(path)
        click.echo(reader.get_file_tree())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


if __name__ == "__main__":
    cli()
