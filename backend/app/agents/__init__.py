"""Product Advisor Specialist Agent Layer.

Decoupled, tool-mediated agents orchestrated by LangGraph:
- SupervisorAgent
- SearchAgent
- ReviewAgent (ReviewAnalysisAgent)
- CompatibilityAgent
- VisionAgent
- RecommendationAgent
"""

from app.agents.compatibility import CompatibilityAgent, compatibility_node
from app.agents.critic import CriticAgent
from app.agents.evidence import EvidenceAgent, evidence_node
from app.agents.parts import PartsAgent, parts_node
from app.agents.query_understanding import QueryUnderstandingAgent, query_understanding_node
from app.agents.recommendation_agent import RecommendationAgent, recommendation_node
from app.agents.review_analysis import ReviewAgent, ReviewAnalysisAgent, review_analysis_node
from app.agents.search_agent import SearchAgent, search_node
from app.agents.supervisor import SupervisorAgent, build_supervisor_graph
from app.agents.vision import VisionAgent, vision_node

__all__ = [
    "SupervisorAgent",
    "SearchAgent",
    "ReviewAgent",
    "ReviewAnalysisAgent",
    "CompatibilityAgent",
    "VisionAgent",
    "RecommendationAgent",
    "CriticAgent",
    "EvidenceAgent",
    "PartsAgent",
    "QueryUnderstandingAgent",
    "build_supervisor_graph",
    "search_node",
    "recommendation_node",
    "review_analysis_node",
    "compatibility_node",
    "vision_node",
    "parts_node",
    "evidence_node",
    "query_understanding_node",
]
