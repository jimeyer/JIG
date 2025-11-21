# @jig C-JIGY-001 implements:S-JIGY-001 subsystem:jigy-tool interface:internal
"""Extract relationships from OSTC node frontmatter and build edges."""

from typing import Any

from jig.core.parser import OSTCNode


# Supported relationship types in JIG v6.1
RELATIONSHIP_TYPES = ["implements", "satisfies", "verifies", "depends_on"]


def extract_relationships_from_node(node: OSTCNode) -> dict[str, list[str]]:
    """Extract relationship fields from node frontmatter metadata.
    
    Extracts implements, satisfies, verifies, and depends_on fields from the node's
    metadata dictionary. Normalizes single values to lists for consistent handling.
    
    Args:
        node: OSTCNode with metadata dictionary
        
    Returns:
        Dictionary mapping relationship type to list of target node IDs
        Example: {"implements": ["O-001", "O-002"], "depends_on": ["S-001"]}
        Returns empty dict if no relationships found.
        
    Example:
        >>> node = OSTCNode(id="S-001", type="specification", title="Test",
        ...                 metadata={"implements": ["O-001", "O-002"]})
        >>> extract_relationships_from_node(node)
        {"implements": ["O-001", "O-002"]}
    """
    if not node.metadata:
        return {}
    
    relationships: dict[str, list[str]] = {}
    
    for rel_type in RELATIONSHIP_TYPES:
        if rel_type in node.metadata:
            value = node.metadata[rel_type]
            
            # Normalize to list
            if isinstance(value, str):
                # Single value - convert to list
                relationships[rel_type] = [value]
            elif isinstance(value, list):
                # Already a list
                relationships[rel_type] = value
            else:
                # Unexpected type - skip (could log warning in production)
                continue
    
    return relationships


def build_edges_from_relationships(
    node_id: str,
    relationships: dict[str, list[str]]
) -> list["Edge"]:
    """Build Edge objects from extracted relationships.
    
    Creates Edge objects for each relationship, where the source is the given node_id
    and the targets are the node IDs in the relationship lists.
    
    Args:
        node_id: Source node ID (e.g., "S-001")
        relationships: Dictionary mapping relationship type to target node IDs
        
    Returns:
        List of Edge objects
        
    Example:
        >>> relationships = {"implements": ["O-001", "O-002"]}
        >>> edges = build_edges_from_relationships("S-001", relationships)
        >>> len(edges)
        2
        >>> edges[0]
        Edge(from_node="S-001", to_node="O-001", type="implements")
    """
    # Import here to avoid circular dependency at module level
    from jig.core.graph import Edge
    
    edges: list[Edge] = []
    
    for rel_type, targets in relationships.items():
        for target in targets:
            edge = Edge(
                from_node=node_id,
                to_node=target,
                type=rel_type
            )
            edges.append(edge)
    
    return edges


def extract_edges_from_node(node: OSTCNode) -> list["Edge"]:
    """Extract all edges from a node's frontmatter relationships.
    
    Convenience function that combines extract_relationships_from_node and
    build_edges_from_relationships.
    
    Args:
        node: OSTCNode with relationship metadata
        
    Returns:
        List of Edge objects representing all relationships in the node
        
    Example:
        >>> node = OSTCNode(id="S-001", type="specification", title="Test",
        ...                 metadata={"implements": ["O-001", "O-002"]})
        >>> edges = extract_edges_from_node(node)
        >>> len(edges)
        2
    """
    relationships = extract_relationships_from_node(node)
    return build_edges_from_relationships(node.id, relationships)

