import click
from aegis.graph.orchestrator import Orchestrator
from aegis.graph.states import OrchestratorInput


@click.group()
def cli():
    """🤖 Autonomous Code Analyst - Evidence-backed codebase analysis

    Philosophy: "If the system can't explain why it said something, it shouldn't say it."
    """
    pass


@cli.command()
@click.argument("path", default=".")
def analyze(path):
    """Full repository analysis (Architecture + Risk)"""
    click.echo(f"🔍 Analyzing repository: {path}\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "analyze",
            "repo_path": path,
            "file_path": None,
            "top_n": None,
            "threshold": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence: {output.confidence:.2f}")
        click.echo(f"📁 Evidence:  {len(output.evidence)} items")

        if output.metadata:
            click.echo(f"🤖 Agents: {', '.join(output.metadata.get('agents_run', []))}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--top", default=10, help="Number of high-risk files to show")
def risk(path, top):
    """Identify high-risk files based on dependencies"""
    click.echo(f"⚠️ Risk Analysis (top {top})\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "risk",
            "repo_path": path,
            "top_n": top,
            "file_path": None,
            "threshold": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence: {output.confidence:.2f}")
        click.echo(f"📁 Evidence: {len(output.evidence)} items")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.option("--path", default=".", help="Path to the code repository")
def overview(path):
    """Architecture overview and layer detection"""
    click.echo("🏗️ Architecture Overview\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "overview",
            "repo_path": path,
            "file_path": None,
            "top_n": None,
            "threshold": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence:  {output.confidence:.2f}")
        click.echo(f"📁 Evidence: {len(output.evidence)} items")

        # Show some evidence
        if output.evidence:
            click.echo("\n📋 Sample Evidence:")
            for evidence in output.evidence[:5]:
                click.echo(f"  • {evidence.file_path}:  {evidence.reason}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("file_path")
@click.option("--path", default=".", help="Path to the code repository")
def deps(file_path, path):
    """Show dependencies for a specific file"""
    click.echo(f"🔗 Dependency Analysis:  {file_path}\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "deps",
            "repo_path": path,
            "file_path": file_path,
            "top_n": None,
            "threshold": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence: {output.confidence:.2f}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("file_path")
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--depth", default=3, help="Maximum depth for impact analysis")
def impact(file_path, path, depth):
    """Analyze blast radius if file changes"""
    click.echo(f"💥 Change Impact Analysis: {file_path}\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "impact",
            "repo_path": path,
            "file_path": file_path,
            "top_n": None,
            "threshold": None,
            "max_depth": depth,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence: {output.confidence:.2f}")

        if output.metadata:
            click.echo(
                f"📊 Blast Radius: {output.metadata.get('total_impact', 0)} files"
            )

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--threshold", default=0.7, help="Confidence threshold (0.0-1.0)")
@click.option("--top", default=20, help="Maximum files to report")
def deadcode(path, threshold, top):
    """Detect probable dead/unused code"""
    click.echo(f"💀 Dead Code Detection (threshold: {threshold})\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "deadcode",
            "repo_path": path,
            "threshold": threshold,
            "top_n": top,
            "file_path": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
            "user_query": None,
        }

        output = orchestrator.execute(input_data)

        # Display analysis
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence:  {output.confidence:.2f}")
        click.echo(f"📁 Evidence: {len(output.evidence)} items")

        if output.metadata:
            click.echo("\n📊 Statistics:")
            click.echo(
                f"  High confidence: {output.metadata.get('high_confidence', 0)}"
            )
            click.echo(
                f"  Medium confidence: {output.metadata.get('medium_confidence', 0)}"
            )

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command("propose-architecture")
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--goal", default="Improve architecture quality", help="Analysis goal")
@click.option("--output", "-o", help="Output file for report (. md)")
def propose_architecture(path, goal, output):
    """Generate architecture improvement proposal (Multi-Agent)"""
    click.echo("🏗️ Architecture Proposal\n")
    click.echo(f"Goal: {goal}\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "propose-architecture",
            "repo_path": path,
            "goal": goal,
            "file_path": None,
            "top_n": None,
            "threshold": None,
            "max_depth": None,
            "diagram_type": None,
            "user_query": None,
        }

        result = orchestrator.execute(input_data)

        # Save to file if specified
        if output:
            with open(output, "w") as f:
                f.write(result.analysis)
            click.echo(f"✅ Report saved to: {output}\n")
        else:
            # Display in terminal
            click.echo("=" * 80)
            click.echo(result.analysis)
            click.echo("=" * 80)

        click.echo(f"\n🎯 Confidence:  {result.confidence:.2f}")
        click.echo(f"📁 Evidence: {len(result.evidence)} items")

        if result.metadata:
            agents = result.metadata.get("agents_run", [])
            click.echo(f"🤖 Agents: {', '.join(agents)}")

            if result.metadata.get("verification_passed"):
                click.echo("✅ Verification:  PASSED")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.option("--path", default=".", help="Path to the code repository")
@click.option(
    "--type",
    "diagram_type",
    type=click.Choice(["architecture", "dependency", "risk"]),
    default="architecture",
    help="Type of diagram to generate",
)
@click.option("--focus", help="Focus on specific layer/module")
@click.option("--output", "-o", help="Output file (. mmd)")
def diagram(path, diagram_type, focus, output):
    """Generate Mermaid diagram"""
    click.echo(f"🎨 Generating {diagram_type} diagram.. .\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        # Generate diagram
        mermaid_code = orchestrator.generate_diagram(diagram_type, focus=focus)

        # Save or display
        if output:
            with open(output, "w") as f:
                f.write(mermaid_code)
            click.echo(f"✅ Diagram saved to: {output}")
            click.echo("💡 View at: https://mermaid.live")
        else:
            click.echo("=" * 80)
            click.echo(mermaid_code)
            click.echo("=" * 80)
            click.echo("\n💡 Copy this to https://mermaid.live to visualize")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("query")
@click.option("--path", default=".", help="Path to the code repository")
def ask(query, path):
    """Ask a question in natural language"""
    click.echo(f"❓ Question: {query}\n")

    try:
        orchestrator = Orchestrator(repo_path=path)

        input_data: OrchestratorInput = {
            "command": "ask",
            "repo_path": path,
            "user_query": query,
            "file_path": None,
            "top_n": None,
            "threshold": None,
            "max_depth": None,
            "goal": None,
            "diagram_type": None,
        }

        output = orchestrator.execute(input_data)

        # Display answer
        click.echo("=" * 80)
        click.echo(output.analysis)
        click.echo("=" * 80)
        click.echo(f"\n🎯 Confidence:  {output.confidence:.2f}")
        click.echo(f"📁 Evidence: {len(output.evidence)} items")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("query")
@click.option("--path", default=".", help="Path to the code repository")
@click.option("--top", default=3, help="Number of results")
def search(query, path, top):
    """Semantic code search"""
    click.echo(f"🔍 Searching for: '{query}'\n")

    try:
        from aegis.mcp_servers.repo_reader.reader import RepoReader
        from aegis.mcp_servers.code_index.index import CodeIndex

        reader = RepoReader(path)
        index = CodeIndex(reader)
        index.build_index()

        results = index.search(query, top_k=top)

        click.echo("=" * 80)
        for i, result in enumerate(results, 1):
            click.echo(f"\n📄 Result {i}:")
            click.echo(f"  File: {result['file']}")
            click.echo(f"  Lines: {result['lines']}")
            if result["name"]:
                click.echo(f"  Name: {result['name']}")
            click.echo("\n  Code Preview:")
            preview = result["code"][:300]
            click.echo(f"  {preview}...")
            click.echo("-" * 80)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument("path", default=".")
def tree(path):
    """Show repository file tree"""
    try:
        from aegis.mcp_servers.repo_reader.reader import RepoReader

        reader = RepoReader(path)
        click.echo(reader.get_file_tree())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


if __name__ == "__main__":
    cli()
