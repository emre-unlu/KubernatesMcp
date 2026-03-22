from __future__ import annotations

from pydoc import text
from typing import Any, Dict, Optional

from clients.base_k8s_client import BaseK8sClient
from clients.jaeger_client import JaegerClient
from clients.neo4j_client import Neo4jClient
from clients.prometheus_client import PrometheusClient
from utils.formatters import short_error


class SystemService:
    """Service for checking backend availability and basic system health."""

    def __init__(
        self,
        k8s_client: BaseK8sClient,
        prometheus_client: Optional[PrometheusClient] = None,
        jaeger_client: Optional[JaegerClient] = None,
        neo4j_client: Optional[Neo4jClient] = None,
    ) -> None:
        self.k8s_client = k8s_client
        self.prometheus_client = prometheus_client
        self.jaeger_client = jaeger_client
        self.neo4j_client = neo4j_client

    def get_backend_status(self) -> Dict[str, Any]:
        return {
            "kubernetes": self._check_kubernetes(),
            "prometheus": self._check_prometheus(),
            "jaeger": self._check_jaeger(),
            "neo4j": self._check_neo4j(),
        }

    def _check_kubernetes(self) -> Dict[str, Any]:
        try:
            pods = self.k8s_client.list_pods()
            services = self.k8s_client.list_services()
            return {
                "available": True,
                "namespace": self.k8s_client.namespace,
                "pod_count": len(pods),
                "service_count": len(services),
            }
        except Exception as exc:
            return {
                "available": False,
                "namespace": self.k8s_client.namespace,
                "error": short_error(exc),
            }

    def _check_prometheus(self) -> Dict[str, Any]:
        if self.prometheus_client is None:
            return {
                "available": False,
                "configured": False,
                "error": "Prometheus client is not configured",
            }

        try:
            ok = self.prometheus_client.is_available()
            return {
                "available": ok,
                "configured": True,
                "url": self.prometheus_client.prometheus_url,
            }
        except Exception as exc:
            return {
                "available": False,
                "configured": True,
                "url": self.prometheus_client.prometheus_url,
                "error": short_error(exc),
            }

    def _check_jaeger(self) -> Dict[str, Any]:
        if self.jaeger_client is None:
            return {
                "available": False,
                "configured": False,
                "error": "Jaeger client is not configured",
            }

        try:
            ok = self.jaeger_client.is_available() if hasattr(self.jaeger_client, "is_available") else False
            return {
                "available": ok,
                "configured": True,
                "url": self.jaeger_client.jaeger_url,
            }
        except Exception as exc:
            return {
                "available": False,
                "configured": True,
                "url": self.jaeger_client.jaeger_url,
                "error": short_error(exc),
            }

    def _check_neo4j(self) -> Dict[str, Any]:
        if self.neo4j_client is None:
            return {
                "available": False,
                "configured": False,
                "error": "Neo4j client is not configured",
            }

        try:
            rows = self.neo4j_client.run_query("RETURN 1 AS ok")
            return {
                "available": True,
                "configured": True,
                "database": self.neo4j_client.database,
                "probe_result": rows,
            }
        except Exception as exc:
            return {
                "available": False,
                "configured": True,
                "database": self.neo4j_client.database,
                "error": short_error(exc),
            }
        
