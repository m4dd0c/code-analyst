from typing import List, Dict, Any, Optional
from aegis.schemas.base import AgentOutput


class MermaidGenerator:
    """
    Mermaid Generator:   Creates valid Mermaid diagrams from structured data.

    CRITICAL RULES:
    - Output ONLY valid Mermaid syntax
    - NO prose, NO markdown wrappers
    - Grounded in actual file paths
    - Never hallucinate nodes or edges

    Supported diagram types:
    - Architecture (flowchart)
    - Dependency graph (graph)
    - Risk matrix (flowchart with colors)
    """

    def __init__(self):
        self.diagram_types = ["architecture", "dependency", "risk"]

    def generate(
        self,
        diagram_type: str,
        data: Dict[str, Any],
        focus: Optional[str] = None,
        max_nodes: int = 30,
    ) -> str:
        """
        Generate Mermaid diagram.

        Args:
            diagram_type: 'architecture' | 'dependency' | 'risk'
            data:  Structured data (layers, graph, risk scores)
            focus: Optional filter (e.g., specific layer or module)
            max_nodes: Maximum nodes to prevent clutter

        Returns:
            Valid Mermaid diagram syntax as string
        """
        if diagram_type not in self.diagram_types:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        if diagram_type == "architecture":
            return self._generate_architecture_diagram(data, focus, max_nodes)
        elif diagram_type == "dependency":
            return self._generate_dependency_diagram(data, focus, max_nodes)
        elif diagram_type == "risk":
            return self._generate_risk_diagram(data, max_nodes)
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

    def _generate_architecture_diagram(
        self, data: Dict[str, Any], focus: Optional[str], max_nodes: int
    ) -> str:
        """
        Generate architecture flowchart.

        Expected data format:
        {
            "layers": {
                "Layer Name": ["file1.py", "file2.py"],
                ...
            },
            "violations": [
                {"source": "file1.py", "target": "file2.py", "type": "... "},
                ...
            ]
        }
        """
        layers = data.get("layers", {})
        violations = data.get("violations", [])

        if not layers:
            return "flowchart TB\n    Empty[No Architecture Data]"

        # Filter by focus if specified
        if focus:
            layers = {k: v for k, v in layers.items() if focus.lower() in k.lower()}

        lines = ["flowchart TB"]

        # Create layer nodes (use first few files as representatives)
        node_id_map = {}
        node_counter = 0

        for layer_name, files in layers.items():
            # Create a node for the layer
            layer_id = f"L{node_counter}"
            node_counter += 1

            # Sanitize layer name for Mermaid
            safe_name = self._sanitize_label(layer_name)
            lines.append(f'    {layer_id}["{safe_name}<br/>({len(files)} files)"]')

            node_id_map[layer_name] = layer_id

            # Add sample files as subnodes (max 3)
            for file_path in files[:3]:
                file_id = f"F{node_counter}"
                node_counter += 1

                safe_file = self._sanitize_label(self._shorten_path(file_path))
                lines.append(f'    {file_id}["{safe_file}"]')
                lines.append(f"    {layer_id} --> {file_id}")

                node_id_map[file_path] = file_id

        # Add layer relationships (typical architecture flow)
        layer_flow = self._infer_layer_flow(list(layers.keys()))
        for source, target in layer_flow:
            if source in node_id_map and target in node_id_map:
                lines.append(f"    {node_id_map[source]} --> {node_id_map[target]}")

        # Add violations (red dashed lines)
        for violation in violations[:5]:  # Max 5 violations
            source = violation.get("source")
            target = violation.get("target")

            if source in node_id_map and target in node_id_map:
                lines.append(
                    f"    {node_id_map[source]} -.->|VIOLATION| {node_id_map[target]}"
                )
                lines.append(f"    style {node_id_map[source]} fill:#ffcccc")
                lines.append(f"    style {node_id_map[target]} fill:#ffcccc")

        # Apply styling
        lines.append("")
        lines.append(
            "    classDef layerNode fill:#e1f5ff,stroke:#01579b,stroke-width:2px"
        )
        for layer_name in layers.keys():
            if layer_name in node_id_map:
                lines.append(f"    class {node_id_map[layer_name]} layerNode")

        return "\n".join(lines)

    def _generate_dependency_diagram(
        self, data: Dict[str, Any], focus: Optional[str], max_nodes: int
    ) -> str:
        """
        Generate dependency graph.

        Expected data format:
        {
            "graph": {
                "file1.py": {
                    "imports": ["file2.py", "file3.py"],
                    "imported_by": ["file0.py"],
                    "fan_in": 1,
                    "fan_out": 2
                },
                ...
            }
        }
        """
        graph_data = data.get("graph", {})

        if not graph_data:
            return "graph TB\n    Empty[No Dependency Data]"

        # Filter by focus
        if focus:
            filtered = {}
            for file_path, file_data in graph_data.items():
                if focus in file_path:
                    filtered[file_path] = file_data
                    # Include immediate dependencies
                    for dep in file_data.get("imports", []):
                        if dep in graph_data:
                            filtered[dep] = graph_data[dep]
            graph_data = filtered

        # Limit nodes
        sorted_files = sorted(
            graph_data.items(),
            key=lambda x: x[1].get("fan_in", 0) + x[1].get("fan_out", 0),
            reverse=True,
        )[:max_nodes]

        lines = ["graph TB"]

        node_id_map = {}
        for i, (file_path, _) in enumerate(sorted_files):
            node_id = f"N{i}"
            node_id_map[file_path] = node_id

            safe_path = self._sanitize_label(self._shorten_path(file_path))
            lines.append(f'    {node_id}["{safe_path}"]')

        # Add edges
        edge_count = 0
        for file_path, file_data in sorted_files:
            if file_path not in node_id_map:
                continue

            source_id = node_id_map[file_path]

            for imported in file_data.get("imports", []):
                if imported in node_id_map and edge_count < max_nodes * 2:
                    target_id = node_id_map[imported]
                    lines.append(f"    {source_id} --> {target_id}")
                    edge_count += 1

        # Style high-risk nodes
        for file_path, file_data in sorted_files:
            if file_path not in node_id_map:
                continue

            fan_in = file_data.get("fan_in", 0)
            node_id = node_id_map[file_path]

            if fan_in >= 5:
                lines.append(
                    f"    style {node_id} fill:#ff9999,stroke:#cc0000,stroke-width:3px"
                )
            elif fan_in >= 3:
                lines.append(
                    f"    style {node_id} fill:#ffcc99,stroke:#ff6600,stroke-width:2px"
                )

        return "\n".join(lines)

    def _generate_risk_diagram(self, data: Dict[str, Any], max_nodes: int) -> str:
        """
        Generate risk matrix flowchart.

        Expected data format:
        {
            "risk_files": [
                {"file":  "file1.py", "score": 0.85, "fan_in": 10},
                ...
            ]
        }
        """
        risk_files = data.get("risk_files", [])

        if not risk_files:
            return "flowchart TB\n    Empty[No Risk Data]"

        # Sort by risk score
        risk_files = sorted(risk_files, key=lambda x: x.get("score", 0), reverse=True)[
            :max_nodes
        ]

        lines = ["flowchart TB"]
        lines.append('    Root["High-Risk Files"]')

        # Group by risk level
        critical = []
        high = []
        medium = []

        for rf in risk_files:
            score = rf.get("score", 0)
            if score >= 0.7:
                critical.append(rf)
            elif score >= 0.5:
                high.append(rf)
            else:
                medium.append(rf)

        node_counter = 0

        # Critical risk
        if critical:
            lines.append('    Critical["🔴 Critical Risk"]')
            lines.append("    Root --> Critical")

            for rf in critical[:5]:
                node_id = f"C{node_counter}"
                node_counter += 1

                file_name = self._shorten_path(rf.get("file", "unknown"))
                score = rf.get("score", 0)
                fan_in = rf.get("fan_in", 0)

                label = f"{file_name}<br/>Score: {score:.2f}<br/>Dependents: {fan_in}"
                safe_label = self._sanitize_label(label)

                lines.append(f'    {node_id}["{safe_label}"]')
                lines.append(f"    Critical --> {node_id}")
                lines.append(
                    f"    style {node_id} fill:#ffcccc,stroke:#cc0000,stroke-width:2px"
                )

        # High risk
        if high:
            lines.append('    High["🟡 High Risk"]')
            lines.append("    Root --> High")

            for rf in high[:5]:
                node_id = f"H{node_counter}"
                node_counter += 1

                file_name = self._shorten_path(rf.get("file", "unknown"))
                score = rf.get("score", 0)
                fan_in = rf.get("fan_in", 0)

                label = f"{file_name}<br/>Score:  {score:.2f}<br/>Dependents: {fan_in}"
                safe_label = self._sanitize_label(label)

                lines.append(f'    {node_id}["{safe_label}"]')
                lines.append(f"    High --> {node_id}")
                lines.append(
                    f"    style {node_id} fill:#fff4cc,stroke:#ff9900,stroke-width:2px"
                )

        # Styling
        lines.append("    style Root fill:#e1f5ff,stroke:#01579b,stroke-width:3px")
        if critical:
            lines.append("    style Critical fill:#ffcccc,stroke:#cc0000")
        if high:
            lines.append("    style High fill:#fff4cc,stroke:#ff9900")

        return "\n".join(lines)

    def _infer_layer_flow(self, layer_names: List[str]) -> List[tuple]:
        """Infer typical architectural flow between layers"""
        flow = []

        # Common patterns
        patterns = [
            ("Interface", "Orchestration"),
            ("Interface", "Agent"),
            ("CLI", "Orchestration"),
            ("CLI", "Agent"),
            ("Orchestration", "Agent"),
            ("Agent", "MCP"),
            ("Agent", "Data"),
            ("MCP", "Schema"),
            ("Data", "Schema"),
        ]

        for source_pattern, target_pattern in patterns:
            source_layer = None
            target_layer = None

            for layer in layer_names:
                if source_pattern.lower() in layer.lower():
                    source_layer = layer
                if target_pattern.lower() in layer.lower():
                    target_layer = layer

            if source_layer and target_layer and source_layer != target_layer:
                flow.append((source_layer, target_layer))

        return flow

    def _sanitize_label(self, text: str) -> str:
        """Sanitize text for Mermaid (escape special chars)"""
        # Replace quotes
        text = text.replace('"', "'")
        # Remove problematic chars
        text = text.replace("[", "(").replace("]", ")")
        return text

    def _shorten_path(self, file_path: str, max_length: int = 30) -> str:
        """Shorten file path for display"""
        if len(file_path) <= max_length:
            return file_path

        # Show first and last parts
        parts = file_path.split("/")
        if len(parts) > 2:
            return f"{parts[0]}/.../{parts[-1]}"

        return file_path[: max_length - 3] + "..."

    def generate_from_agent_output(
        self, agent_output: AgentOutput, diagram_type: str
    ) -> str:
        """
        Generate diagram directly from AgentOutput.

        This extracts structured data from metadata or evidence.
        """
        data = {}

        if diagram_type == "architecture":
            # Extract layers from metadata or evidence
            if agent_output.metadata and "layers" in agent_output.metadata:
                data["layers"] = agent_output.metadata["layers"]
            else:
                # Infer from evidence
                data["layers"] = self._infer_layers_from_evidence(agent_output.evidence)

            data["violations"] = agent_output.metadata.get("violations", [])

        elif diagram_type == "dependency":
            # Extract graph from metadata
            if agent_output.metadata and "graph" in agent_output.metadata:
                data["graph"] = agent_output.metadata["graph"]
            else:
                data["graph"] = {}

        elif diagram_type == "risk":
            # Extract risk files from evidence
            risk_files = []
            for evidence in agent_output.evidence:
                if (
                    "risk" in evidence.reason.lower()
                    or "score" in evidence.reason.lower()
                ):
                    # Parse risk score from reason
                    score = 0.5  # default
                    fan_in = 0

                    # Simple parsing (can be improved)
                    if "score" in evidence.reason.lower():
                        try:
                            score_part = [
                                p for p in evidence.reason.split() if "0." in p
                            ][0]
                            score = float(score_part)
                        except Exception:
                            pass

                    risk_files.append(
                        {
                            "file": evidence.file_path,
                            "score": score,
                            "fan_in": fan_in,
                        }
                    )

            data["risk_files"] = risk_files

        return self.generate(diagram_type, data)

    def _infer_layers_from_evidence(self, evidence: List) -> Dict[str, List[str]]:
        """Infer layers from evidence by grouping file paths"""
        layers = {}

        for ev in evidence:
            file_path = ev.file_path
            if "/" in file_path:
                layer = file_path.split("/")[0]
                if layer not in layers:
                    layers[layer] = []
                layers[layer].append(file_path)

        return layers
