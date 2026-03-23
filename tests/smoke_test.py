from __future__ import annotations

from app.dependencies import (
    get_logs_service,
    get_metrics_service,
    get_shell_service,
    get_system_service,
    get_topology_service,
    get_trace_service,
)


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def print_backend_status() -> None:
    system_service = get_system_service()
    status = system_service.get_backend_status()

    for name, info in status.items():
        available = info.get("available", False)
        configured = info.get("configured", True)
        marker = "OK" if available else "DOWN"
        error = info.get("error")
        url = info.get("url")
        extra = []

        if url:
            extra.append(f"url={url}")
        if "namespace" in info:
            extra.append(f"namespace={info['namespace']}")
        if "pod_count" in info:
            extra.append(f"pods={info['pod_count']}")
        if "service_count" in info:
            extra.append(f"services={info['service_count']}")
        if error:
           extra.append(f"error={error}")

        print(f"{name:12} | status={marker} | configured={configured} | " + " | ".join(extra))


def print_topology_summary() -> None:
    topology_service = get_topology_service()

    overview = topology_service.get_cluster_overview(namespace="kube-system")
    print(
        f"namespace={overview['namespace']} "
        f"pods={overview['pod_count']} services={overview['service_count']}"
    )

    mapping = topology_service.get_pods_from_service("kube-dns", namespace="kube-system")
    pod_names = [pod["pod_name"] for pod in mapping.get("pods", [])]
    print(f"service kube-dns -> pods: {pod_names}")

    reverse = topology_service.get_services_from_pod(
        "coredns-7d764666f9-q5rkz",
        namespace="kube-system",
    )
    service_names = [svc["service_name"] for svc in reverse.get("services", [])]
    print(f"pod coredns-7d764666f9-q5rkz -> services: {service_names}")

    print("=== Service dependencies for 'frontend' ===")

    print(topology_service.get_service_dependencies("frontend"))
    print(topology_service.get_service_map("frontend", depth=2))


def print_logs_summary() -> None:
    logs_service = get_logs_service()

    pod_logs = logs_service.get_pod_logs(
        "coredns-7d764666f9-q5rkz",
        namespace="kube-system",
        important_only=False,
    )
    print(f"pod log lines: {pod_logs.get('line_count', 0)}")
    print(f"first 3 lines: {pod_logs.get('lines', [])[:3]}")

    service_logs = logs_service.summarize_service_logs(
        "kube-dns",
        namespace="kube-system",
    )
    print(f"service logs summary: {service_logs.get('summary', {})}")


def print_metrics_summary() -> None:
    metrics_service = get_metrics_service()

    pod_metrics = metrics_service.get_pod_metrics(
        "coredns-7d764666f9-q5rkz",
        namespace="kube-system",
    )
    print(f"pod metrics: {pod_metrics.get('metrics', {})}")

    service_metrics = metrics_service.get_service_metrics(
        "kube-dns",
        namespace="kube-system",
    )
    print(f"aggregated service metrics: {service_metrics.get('aggregated_metrics', {})}")


def print_shell_summary() -> None:
    shell_service = get_shell_service()

    policy = shell_service.get_shell_policy()
    print(
        f"shell timeout={policy['timeout_seconds']} "
        f"allowed={policy['allowed_prefixes']}"
    )

    result = shell_service.exec_kubectl("kubectl get pods -n kube-system")
    print(
        f"kubectl success={result.get('success')} "
        f"exit_code={result.get('exit_code')} "
        f"stdout_lines={result.get('summary', {}).get('stdout_line_count')}"
    )

def print_trace_summary() -> None:
    trace_service = get_trace_service()

    print("=== Trace summaries for 'frontend' ===")

    trace_service = get_trace_service()
    print(trace_service.get_trace_summaries("jaeger-all-in-one"))


def main() -> None:
    print_section("backend status")
    print_backend_status()

    print_section("topology")
    print_topology_summary()

    print_section("logs")
    print_logs_summary()

    print_section("metrics")
    print_metrics_summary()

    print_section("shell")
    print_shell_summary()

    print_section("traces")
    print_trace_summary()


if __name__ == "__main__":
    main()