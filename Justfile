# =============================================================================
# C:\src\yolo\packages\gitingest Sovereign Justfile (uv v0.13.7+ & Ruff Google)
# =============================================================================

set shell := ["nu", "-c"]
set windows-shell := ["nu", "-c"]

default:
    @just --list

# Sync uv virtual environment and dependencies
sync:
    @uv sync

# Run Ruff linter enforcing Google Python Style Guide
lint:
    @uv run ruff check src tests

# Format Python code via Ruff
fmt:
    @uv run ruff format src tests

# Run pytest suite
test:
    @uv run pytest tests/test_yolo_fleet.py

# Ingest a repository or directory via gitingest CLI
gitingest target="." output="digest.txt":
    @uv run gitingest {{target}} -o {{output}}

# Deep-search across local monorepo or ingested digest
deep-search query target="C:/src":
    @rg -n --hidden --glob "!.git" --glob "!node_modules" --glob "!target" "{{query}}" {{target}}

# Fact-check monorepo inventory and docs compliance
fact-check:
    @bun run C:/src/docs/scripts/git-ingest-and-fact-check.ts
    @bun test C:/src/docs/scripts/fact-check-docs.test.ts

# Fast-forward Git sync across all C:\src pillars
git-sync:
    @bun run C:/src/yolo/scripts/yolo-git.ts sync

# Sync yolo-rs/gitingest fork with coderamp-labs/gitingest upstream
fork-sync:
    @git fetch upstream; git merge --ff-only upstream/main

# Inspect and sync Google depot_tools (gclient, git-cl, repo)
depot-sync:
    @uv run python -c "from gitingest.yolo_fleet import inspect_depot_tools; import json, dataclasses; print(json.dumps(dataclasses.asdict(inspect_depot_tools()), indent=2))"

# Generate full Upstream Ecosystem & Linux Distro Matrix JSON report
stack-matrix:
    @uv run python -c "from gitingest.yolo_fleet import build_ecosystem_matrix_report; print(build_ecosystem_matrix_report().to_json())"

# Output Arch Linux / CachyOS / SteamOS / YOLO-OS pacman.conf repository stanzas
arch-repos:
    @uv run python -c "from gitingest.yolo_fleet import generate_pacman_conf_snippet; print(generate_pacman_conf_snippet(), end='')"
