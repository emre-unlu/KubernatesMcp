from __future__ import annotations

from app.dependencies import get_system_service
from app.server import mcp


@mcp.tool()
def get_backend_status():
    """Return availability status for Kubernetes, Prometheus, Jaeger, and Neo4j."""
    service = get_system_service()
    return service.get_backend_status()