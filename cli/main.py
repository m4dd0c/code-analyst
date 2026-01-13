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
