"""Optional MLflow tracing for the LangChain/Groq chains.

Off unless MLFLOW_TRACING_ENABLED=true, so the app and tests never import
mlflow by default. Tracing must never take the app down: any setup failure
is logged and swallowed.

Privacy: traces record prompts and outputs. The explain prompt is public
transcript text; the strategy-overview prompt carries only the coarse
risk-profile/experience labels. No user ids, tokens or request bodies reach
a chain, so none end up in a trace.
"""

from __future__ import annotations

import logging

from config import get_settings

logger = logging.getLogger(__name__)


def init_tracing() -> bool:
    """Enable MLflow LangChain autologging. Returns True if tracing is on."""
    settings = get_settings()
    if not settings.mlflow_tracing_enabled:
        return False
    try:
        import mlflow

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)
        mlflow.langchain.autolog()
    except Exception:  # noqa: BLE001 - observability is optional
        logger.exception("MLflow tracing setup failed; continuing without tracing")
        return False
    logger.info("MLflow tracing enabled (experiment=%s)", settings.mlflow_experiment_name)
    return True
