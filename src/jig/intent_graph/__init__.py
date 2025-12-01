"""Intent graph generation module.

Generates intent-graph.ndjson from specifications, outcomes, and bricks.yaml.
"""

from .generator import generate_intent_graph

__all__ = ["generate_intent_graph"]
