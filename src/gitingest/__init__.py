"""Gitingest: A package for ingesting data from Git repositories."""

from gitingest.entrypoint import ingest, ingest_async
from gitingest.yolo_fleet import (
    ArchCustomRepo,
    DepotToolsStatus,
    EcosystemMatrixReport,
    FleetRepoEntry,
    UpstreamDomainSpec,
    build_arch_custom_repositories,
    build_ecosystem_matrix_report,
    build_upstream_domains,
    generate_pacman_conf_snippet,
    inspect_depot_tools,
    scan_yolo_fleet_inventory,
)

__all__ = [
    "ArchCustomRepo",
    "DepotToolsStatus",
    "EcosystemMatrixReport",
    "FleetRepoEntry",
    "UpstreamDomainSpec",
    "build_arch_custom_repositories",
    "build_ecosystem_matrix_report",
    "build_upstream_domains",
    "generate_pacman_conf_snippet",
    "ingest",
    "ingest_async",
    "inspect_depot_tools",
    "scan_yolo_fleet_inventory",
]
