"""Sovereign YOLO Fleet & Upstream Ecosystem Matrix integration for Gitingest.

This module provides Google Python Style Guide compliant tooling to integrate:
1. ``C:/src/depot_tools`` (gclient, git-cl, repo, Chromium/Google OSS sync).
2. Root ``C:/src`` 9 ``yolo*`` pillars + ``google`` + ``apps/{shenron,rosegriffon,aphrody}``
   inventory, AST/Git parsing, fact-checking, and ``yolo-rs`` fork management.
3. Upstream ecosystem and Linux distro matrix builder and analyzer covering:
   - Google OSS (google, google-labs-code, Chromium/depot_tools, Material 3, Abseil/Rust)
   - Vercel & Vercel Labs (vercel, vercel-labs/skills, agent-skills, fx, native, vinext)
   - Unreal Engine 6 (EpicGames/UnrealEngine, yolo-engine, Commit.gitdeps.xml, 46 forks, EOS)
   - Linux Kernel & Distros (torvalds/linux 7.2/7.3, ValveSoftware/SteamOS + gamescope,
     basecamp/omarchy, CachyOS/linux-cachyos BORE/LTO/PGO/sched-ext, Arch Linux custom repos).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_SRC_ROOT = Path("C:/src")
DEFAULT_DEPOT_TOOLS_PATH = Path("C:/src/depot_tools")

NINE_YOLO_PILLARS: tuple[str, ...] = (
    "yolo",
    "yolo-engine",
    "yolo-ui",
    "yolo-web",
    "yolo-backend",
    "yolo-vps",
    "yolo-cloudflare",
    "yolo-stack",
    "yolo-os",
)

EXTENDED_FLEET_REPOS: tuple[str, ...] = (
    *NINE_YOLO_PILLARS,
    "google",
    "apps/shenron",
    "apps/rosegriffon",
    "apps/aphrody",
)


@dataclass(frozen=True, slots=True)
class DepotToolsStatus:
    """Status and binary availability of Google depot_tools in C:/src/depot_tools.

    Attributes:
        root_path: Canonical filesystem path to depot_tools.
        exists: Whether the depot_tools directory exists on disk.
        binaries: Mapping of tool name (gclient, git-cl, repo, gn, autoninja, cipd)
            to boolean availability.
        head_commit: Current Git HEAD short SHA of depot_tools if available.
    """

    root_path: str
    exists: bool
    binaries: dict[str, bool]
    head_commit: str | None = None


@dataclass(frozen=True, slots=True)
class FleetRepoEntry:
    """Inventory metadata for a sovereign repository or application pillar in C:/src.

    Attributes:
        name: Logical pillar or application identifier.
        path: Canonical forward-slash path on disk.
        exists: Whether the directory exists locally.
        has_git: Whether a .git directory or file is present.
        cargo_manifests: Count of discovered Cargo.toml files (up to depth 2).
        bun_packages: Count of discovered package.json files (up to depth 2).
        python_projects: Count of discovered pyproject.toml files (up to depth 2).
        yolo_rs_remote: Configured origin or yolo-rs Git remote URL if detected.
    """

    name: str
    path: str
    exists: bool
    has_git: bool
    cargo_manifests: int
    bun_packages: int
    python_projects: int
    yolo_rs_remote: str | None = None


@dataclass(frozen=True, slots=True)
class ArchCustomRepo:
    """Configuration entry for an Arch Linux / SteamOS / CachyOS pacman repository.

    Attributes:
        name: Pacman repository stanza name (e.g., ``[cachyos-v4]``).
        architecture: Target CPU ISA tier (e.g., ``x86_64_v4``, ``x86_64_v3``, ``x86_64``).
        server_url: Canonical mirrorlist or Server URL template.
        sig_level: Pacman SigLevel directive.
        purpose: Summary of packages supplied by this repository.
    """

    name: str
    architecture: str
    server_url: str
    sig_level: str
    purpose: str


@dataclass(frozen=True, slots=True)
class UpstreamDomainSpec:
    """Specification of an upstream open-source domain tracked by the YOLO Fleet.

    Attributes:
        domain_id: Short slug identifier for the domain.
        title: Human-readable domain title.
        upstream_orgs: Upstream GitHub organizations or Git hosts.
        key_repositories: Canonical upstream repositories tracked or forked.
        local_integration_paths: Paths under C:/src integrating this domain.
        key_technologies: Core technologies, patches, or protocols verified.
    """

    domain_id: str
    title: str
    upstream_orgs: list[str]
    key_repositories: list[str]
    local_integration_paths: list[str]
    key_technologies: list[str]


@dataclass(frozen=True, slots=True)
class EcosystemMatrixReport:
    """Complete sovereign fleet and upstream ecosystem matrix analysis report.

    Attributes:
        depot_tools: Status of Google depot_tools.
        fleet_inventory: Inventory of the 9 yolo* pillars + google + 3 apps.
        upstream_domains: Four canonical upstream ecosystem domains.
        arch_repositories: Custom Arch Linux / CachyOS / SteamOS / YOLO-OS repositories.
        summary_stats: Aggregated numerical metrics across the fleet.
    """

    depot_tools: DepotToolsStatus
    fleet_inventory: list[FleetRepoEntry]
    upstream_domains: list[UpstreamDomainSpec]
    arch_repositories: list[ArchCustomRepo]
    summary_stats: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the matrix report to a JSON-compatible dictionary.

        Returns:
            A nested dictionary representation of the report.
        """
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize the matrix report to a formatted JSON string.

        Args:
            indent: Number of spaces for JSON indentation.

        Returns:
            Formatted JSON string.
        """
        return json.dumps(self.to_dict(), indent=indent)


def inspect_depot_tools(depot_path: Path = DEFAULT_DEPOT_TOOLS_PATH) -> DepotToolsStatus:
    """Inspect Google depot_tools installation and available workflows.

    Checks for ``gclient``, ``git-cl``, ``repo``, ``gn``, ``autoninja``, and ``cipd``
    inside ``C:/src/depot_tools`` and resolves the current Git HEAD commit if available.

    Args:
        depot_path: Filesystem path to the depot_tools checkout.

    Returns:
        A populated ``DepotToolsStatus`` instance.
    """
    exists = depot_path.is_dir()
    tools = ("gclient", "git-cl", "repo", "gn", "autoninja", "cipd", "vpython3")
    binaries: dict[str, bool] = {}

    for tool in tools:
        if not exists:
            binaries[tool] = False
            continue
        candidates = (
            depot_path / tool,
            depot_path / f"{tool}.py",
            depot_path / f"{tool}.bat",
        )
        binaries[tool] = any(c.exists() for c in candidates)

    head_commit: str | None = None
    if exists and (depot_path / ".git").exists():
        try:
            proc = subprocess.run(
                ["git", "-C", str(depot_path), "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if proc.returncode == 0:
                head_commit = proc.stdout.strip()
        except OSError:
            head_commit = None

    return DepotToolsStatus(
        root_path=depot_path.as_posix(),
        exists=exists,
        binaries=binaries,
        head_commit=head_commit,
    )


def _count_files_up_to_depth(root: Path, filename: str, max_depth: int = 2) -> int:
    """Count occurrences of a target filename up to a maximum directory depth.

    Args:
        root: Base directory to scan.
        filename: Exact file name to match (e.g., ``Cargo.toml``).
        max_depth: Maximum recursion depth relative to ``root``.

    Returns:
        Total number of matching files discovered.
    """
    if not root.is_dir():
        return 0

    ignored_dirs = {
        ".git",
        "node_modules",
        "target",
        "vendor",
        "artifacts",
        "dist",
        "upstream",
        ".venv",
        "__pycache__",
    }
    count = 0

    def _walk(current: Path, depth: int) -> None:
        nonlocal count
        if depth > max_depth:
            return
        try:
            for entry in current.iterdir():
                if entry.name in ignored_dirs:
                    continue
                if entry.is_dir():
                    _walk(entry, depth + 1)
                elif entry.name == filename:
                    count += 1
        except OSError:
            return

    _walk(root, 0)
    return count


def _read_git_origin(repo_path: Path) -> str | None:
    """Read the origin remote URL of a Git repository without spawning a shell if possible.

    Args:
        repo_path: Path to the repository root.

    Returns:
        The origin remote URL string if found, otherwise ``None``.
    """
    git_config = repo_path / ".git" / "config"
    if not git_config.is_file():
        return None
    try:
        content = git_config.read_text(encoding="utf-8", errors="ignore")
        in_origin = False
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("[") and line.endswith("]"):
                in_origin = line == '[remote "origin"]'
            elif in_origin and line.startswith("url"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    return parts[1].strip()
    except OSError:
        return None
    return None


def scan_yolo_fleet_inventory(src_root: Path = DEFAULT_SRC_ROOT) -> list[FleetRepoEntry]:
    """Scan the 9 canonical yolo* pillars, google monorepo, and 3 sovereign apps.

    Args:
        src_root: Root directory housing the sovereign fleet (defaults to ``C:/src``).

    Returns:
        List of ``FleetRepoEntry`` objects describing each pillar and app.
    """
    entries: list[FleetRepoEntry] = []
    for rel_name in EXTENDED_FLEET_REPOS:
        repo_path = src_root / rel_name
        exists = repo_path.is_dir()
        has_git = exists and (repo_path / ".git").exists()
        cargo_count = _count_files_up_to_depth(repo_path, "Cargo.toml", max_depth=2)
        bun_count = _count_files_up_to_depth(repo_path, "package.json", max_depth=2)
        py_count = _count_files_up_to_depth(repo_path, "pyproject.toml", max_depth=2)
        origin = _read_git_origin(repo_path) if has_git else None

        entries.append(
            FleetRepoEntry(
                name=rel_name,
                path=repo_path.as_posix(),
                exists=exists,
                has_git=has_git,
                cargo_manifests=cargo_count,
                bun_packages=bun_count,
                python_projects=py_count,
                yolo_rs_remote=origin,
            )
        )
    return entries


def build_upstream_domains() -> list[UpstreamDomainSpec]:
    """Build the canonical 4-domain upstream ecosystem specification matrix.

    Covers:
    1. Google OSS (google, google-labs-code, Chromium/depot_tools, Material 3, Abseil/Rust).
    2. Vercel & Vercel Labs (vercel, skills, agent-skills, fx, native, cloudflare/vinext).
    3. Unreal Engine 6 (EpicGames/UnrealEngine, yolo-engine, Commit.gitdeps.xml, 46 forks, EOS).
    4. Linux Kernel & Distros (torvalds/linux 7.2/7.3, SteamOS, Omarchy, CachyOS, Arch Linux).

    Returns:
        List of four ``UpstreamDomainSpec`` records.
    """
    return [
        UpstreamDomainSpec(
            domain_id="google-oss",
            title="Google Open Source, Chromium M156-M158 & depot_tools",
            upstream_orgs=["google", "google-labs-code", "chromium", "abseil"],
            key_repositories=[
                "chromium/tools/depot_tools",
                "chromium/src",
                "google/material-design-icons",
                "google/comprehensive-rust",
                "abseil/abseil-cpp",
                "coderamp-labs/gitingest",
            ],
            local_integration_paths=[
                "C:/src/depot_tools",
                "C:/src/google",
                "C:/src/yolo/packages/gitingest",
                "C:/src/yolo-ui",
            ],
            key_technologies=[
                "depot_tools (gclient, git-cl, repo, gn, autoninja, cipd)",
                "Chromium M156 stable / M157 dev / M158 canary via yolo cvm",
                "Material 3 HCT / CAM16 chromatic system in yolo-ui",
                "Google Python Style Guide & Abseil/Rust safety invariants",
            ],
        ),
        UpstreamDomainSpec(
            domain_id="vercel-and-labs",
            title="Vercel, Vercel Labs & Cloudflare Vinext Meta-Framework",
            upstream_orgs=["vercel", "vercel-labs", "cloudflare"],
            key_repositories=[
                "vercel/next.js",
                "vercel/ai",
                "vercel-labs/skills",
                "vercel-labs/agent-skills",
                "vercel-labs/fx",
                "vercel-labs/native",
                "cloudflare/vinext",
            ],
            local_integration_paths=[
                "C:/src/yolo-stack",
                "C:/src/yolo/packages/plugins",
                "C:/src/apps/shenron",
                "C:/src/apps/rosegriffon",
                "C:/src/apps/aphrody",
            ],
            key_technologies=[
                "Next.js 16.5 Standalone + cloudflare/vinext multi-target compiler",
                "vercel-labs/skills & agent-skills unified in yolo-plugins",
                "Zero Node.js / 100% Pure Bun v1.4.4+ runtime execution",
                "Edge workerd + Pingora 0.9.1 gateway parity",
            ],
        ),
        UpstreamDomainSpec(
            domain_id="unreal-engine-6",
            title="Unreal Engine 6 (EpicGames/UnrealEngine & YOLO Engine 6.0)",
            upstream_orgs=["EpicGames", "yolo-rs"],
            key_repositories=[
                "EpicGames/UnrealEngine",
                "yolo-rs/yolo-engine",
                "yolo-rs/bevy",
                "yolo-rs/zed",
                "yolo-rs/wgpu",
                "yolo-rs/tree-sitter",
            ],
            local_integration_paths=[
                "C:/src/yolo-engine",
                "/srv/build/sources/unreal-engine-6-lite",
            ],
            key_technologies=[
                "Commit.gitdeps.xml & UBT/UAT deterministic build parity",
                "46 sovereign yolo-rs Rust 2024 forks (Bevy, Zed GPUI 0.8, wgpu v30)",
                "Epic Online Services (EOS) C11/C++20/Rust/TS SDK + FOfflineGameOwnershipReceipt",
                "Criware (.cpk, .usm, .acb), Level-5 (.g4tx, .g4mg), Bandai Namco UE4/5/6 porters",
                "11 platform SDKs & 8 store publishing channels",
            ],
        ),
        UpstreamDomainSpec(
            domain_id="linux-kernel-and-distros",
            title="Linux Kernel 7.2/7.3, SteamOS, Omarchy, CachyOS & Arch Linux",
            upstream_orgs=[
                "torvalds",
                "ValveSoftware",
                "basecamp",
                "CachyOS",
                "archlinux",
            ],
            key_repositories=[
                "torvalds/linux",
                "ValveSoftware/SteamOS",
                "ValveSoftware/gamescope",
                "ValveSoftware/steamos-customizations",
                "basecamp/omarchy",
                "CachyOS/linux-cachyos",
                "CachyOS/CachyOS-PKGBUILDS",
            ],
            local_integration_paths=[
                "C:/src/yolo-os",
                "C:/src/yolo-ui",
                "C:/src/yolo-vps",
            ],
            key_technologies=[
                "Linux 7.2/7.3 LTS/mainline + Asterinas Framekernel + Rust Binder IPC",
                "CachyOS BORE scheduler, LTO/PGO/BOLT, sched-ext (scx_lavd, scx_rusty)",
                "Valve SteamOS gamescope Wayland micro-compositor & jupiter-staging",
                "Basecamp Omarchy Hyprland configs & chromatic theme presets in yolo-ui",
                "Arch Linux x86-64-v3 / x86-64-v4 optimized package tiers",
            ],
        ),
    ]


def build_arch_custom_repositories() -> list[ArchCustomRepo]:
    """Build the canonical list of Arch Linux, CachyOS, SteamOS, and YOLO-OS repositories.

    Returns:
        List of ``ArchCustomRepo`` specifications for ``/etc/pacman.conf``.
    """
    return [
        ArchCustomRepo(
            name="[cachyos-v4]",
            architecture="x86_64_v4",
            server_url="https://mirror.cachyos.org/repo/$arch_v4/$repo",
            sig_level="Required DatabaseOptional",
            purpose="AVX-512 / x86-64-v4 PGO+LTO optimized CachyOS core packages and BORE kernels",
        ),
        ArchCustomRepo(
            name="[cachyos-v3]",
            architecture="x86_64_v3",
            server_url="https://mirror.cachyos.org/repo/$arch_v3/$repo",
            sig_level="Required DatabaseOptional",
            purpose="AVX2 / x86-64-v3 optimized CachyOS packages and sched-ext schedulers",
        ),
        ArchCustomRepo(
            name="[cachyos]",
            architecture="x86_64",
            server_url="https://mirror.cachyos.org/repo/$arch/$repo",
            sig_level="Required DatabaseOptional",
            purpose="Baseline CachyOS kernel, proton-cachyos, and system utilities",
        ),
        ArchCustomRepo(
            name="[chaotic-aur]",
            architecture="x86_64",
            server_url="https://cdn-mirror.chaotic.cx/$repo/$arch",
            sig_level="Required DatabaseOptional",
            purpose="Pre-built AUR binaries for developer toolchains, Wayland, and gaming",
        ),
        ArchCustomRepo(
            name="[jupiter-staging]",
            architecture="x86_64",
            server_url="https://steamdeck-packages.steamos.cloud/archlinux-mirror/$repo/os/$arch",
            sig_level="Required DatabaseOptional",
            purpose="Valve SteamOS Holo / Jupiter gamescope, mesa-radv, and steamos-customizations",
        ),
        ArchCustomRepo(
            name="[yolo-os]",
            architecture="x86_64_v4",
            server_url="https://cdn.aphrody.com/arch/$repo/$arch",
            sig_level="Required TrustedOnly",
            purpose="Sovereign YOLO-OS kernel, Bun v1.4.4+ AOT, GPUI Zed/Craft, and YOLO Engine",
        ),
    ]


def generate_pacman_conf_snippet() -> str:
    """Generate a ready-to-include pacman.conf snippet for all sovereign Arch repositories.

    Returns:
        Multi-line configuration string formatted for ``/etc/pacman.conf``.
    """
    lines: list[str] = [
        "# Sovereign YOLO-OS / CachyOS / SteamOS / Chaotic-AUR Pacman Configuration",
        "# Architecture: x86_64 x86_64_v3 x86_64_v4",
        "",
    ]
    for repo in build_arch_custom_repositories():
        lines.extend(
            [
                f"# {repo.purpose}",
                repo.name,
                f"SigLevel = {repo.sig_level}",
                f"Server = {repo.server_url}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_ecosystem_matrix_report(
    src_root: Path = DEFAULT_SRC_ROOT,
    depot_path: Path = DEFAULT_DEPOT_TOOLS_PATH,
) -> EcosystemMatrixReport:
    """Build the complete sovereign YOLO Fleet and upstream ecosystem matrix report.

    Args:
        src_root: Root directory containing the sovereign repositories.
        depot_path: Directory containing Google depot_tools.

    Returns:
        A fully populated ``EcosystemMatrixReport`` instance.
    """
    depot = inspect_depot_tools(depot_path)
    inventory = scan_yolo_fleet_inventory(src_root)
    domains = build_upstream_domains()
    arch_repos = build_arch_custom_repositories()

    summary_stats = {
        "total_fleet_entries": len(inventory),
        "existing_fleet_entries": sum(1 for item in inventory if item.exists),
        "git_enabled_repos": sum(1 for item in inventory if item.has_git),
        "total_cargo_manifests": sum(item.cargo_manifests for item in inventory),
        "total_bun_packages": sum(item.bun_packages for item in inventory),
        "total_python_projects": sum(item.python_projects for item in inventory),
        "upstream_domains_count": len(domains),
        "arch_custom_repos_count": len(arch_repos),
        "depot_tools_available_binaries": sum(1 for ok in depot.binaries.values() if ok),
    }

    return EcosystemMatrixReport(
        depot_tools=depot,
        fleet_inventory=inventory,
        upstream_domains=domains,
        arch_repositories=arch_repos,
        summary_stats=summary_stats,
    )
