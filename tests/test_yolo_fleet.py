"""Unit tests for the sovereign YOLO Fleet & Upstream Ecosystem Matrix module."""

from __future__ import annotations

import json
from pathlib import Path

from gitingest.yolo_fleet import (
    EXTENDED_FLEET_REPOS,
    NINE_YOLO_PILLARS,
    build_arch_custom_repositories,
    build_ecosystem_matrix_report,
    build_upstream_domains,
    generate_pacman_conf_snippet,
    inspect_depot_tools,
    scan_yolo_fleet_inventory,
)


def test_nine_yolo_pillars_and_extended_fleet() -> None:
    assert len(NINE_YOLO_PILLARS) == 9
    assert "yolo" in NINE_YOLO_PILLARS
    assert "yolo-engine" in NINE_YOLO_PILLARS
    assert "yolo-os" in NINE_YOLO_PILLARS
    assert "google" in EXTENDED_FLEET_REPOS
    assert "apps/shenron" in EXTENDED_FLEET_REPOS
    assert "apps/rosegriffon" in EXTENDED_FLEET_REPOS
    assert "apps/aphrody" in EXTENDED_FLEET_REPOS


def test_inspect_depot_tools(tmp_path: Path) -> None:
    fake_depot = tmp_path / "depot_tools"
    fake_depot.mkdir()
    (fake_depot / "gclient").write_text("#!/bin/sh\n", encoding="utf-8")
    (fake_depot / "git-cl.py").write_text("# python\n", encoding="utf-8")
    (fake_depot / "repo").write_text("# repo\n", encoding="utf-8")

    status = inspect_depot_tools(fake_depot)
    assert status.exists is True
    assert status.binaries["gclient"] is True
    assert status.binaries["git-cl"] is True
    assert status.binaries["repo"] is True
    assert status.binaries["autoninja"] is False


def test_scan_yolo_fleet_inventory(tmp_path: Path) -> None:
    yolo_dir = tmp_path / "yolo"
    yolo_dir.mkdir()
    (yolo_dir / ".git").mkdir()
    (yolo_dir / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/yolo-rs/yolo.git\n',
        encoding="utf-8",
    )
    (yolo_dir / "package.json").write_text("{}", encoding="utf-8")
    (yolo_dir / "Cargo.toml").write_text("[workspace]\n", encoding="utf-8")

    inventory = scan_yolo_fleet_inventory(tmp_path)
    assert len(inventory) == len(EXTENDED_FLEET_REPOS)
    yolo_entry = next(item for item in inventory if item.name == "yolo")
    assert yolo_entry.exists is True
    assert yolo_entry.has_git is True
    assert yolo_entry.cargo_manifests == 1
    assert yolo_entry.bun_packages == 1
    assert yolo_entry.yolo_rs_remote == "https://github.com/yolo-rs/yolo.git"


def test_upstream_domains_and_arch_repos() -> None:
    domains = build_upstream_domains()
    domain_ids = [d.domain_id for d in domains]
    assert domain_ids == [
        "google-oss",
        "vercel-and-labs",
        "unreal-engine-6",
        "linux-kernel-and-distros",
    ]

    arch_repos = build_arch_custom_repositories()
    repo_names = [r.name for r in arch_repos]
    assert "[cachyos]" in repo_names
    assert "[cachyos-v3]" in repo_names
    assert "[cachyos-v4]" in repo_names
    assert "[chaotic-aur]" in repo_names
    assert "[jupiter-staging]" in repo_names
    assert "[yolo-os]" in repo_names

    snippet = generate_pacman_conf_snippet()
    assert "[cachyos-v4]" in snippet
    assert "[jupiter-staging]" in snippet
    assert "[yolo-os]" in snippet


def test_build_ecosystem_matrix_report_json(tmp_path: Path) -> None:
    report = build_ecosystem_matrix_report(src_root=tmp_path, depot_path=tmp_path / "depot_tools")
    raw_json = report.to_json()
    parsed = json.loads(raw_json)
    assert parsed["summary_stats"]["upstream_domains_count"] == 4
    assert parsed["summary_stats"]["arch_custom_repos_count"] == 6
