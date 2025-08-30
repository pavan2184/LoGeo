"""
Backend package for Geo-Compliance Detection System

This package contains all the core backend modules for the geo-compliance detection system,
including decision engines, classifiers, and supporting utilities.
"""

# Package version
__version__ = "1.0.0"

# Make key classes available at package level for easier imports
try:
    from .enhanced_decision_engine import EnhancedDecisionEngine
    from .llm_classifier import LLMClassifier
    from .enhanced_classifier import EnhancedClassifier
    from .rag_loader import RegulationRAG
    from .geo_compliance import GeoComplianceEngine
except ImportError:
    # Handle import errors gracefully during development
    pass
