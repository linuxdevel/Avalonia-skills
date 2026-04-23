#!/usr/bin/env bash
# Avalonia Skills Installer
# Installs Avalonia AI agent skills into all detected agent skill directories.
#
# Usage:
#   curl -LsSf https://raw.githubusercontent.com/linuxdevel/Avalonia-skills/main/install.sh | bash
#
# Or locally:
#   ./install.sh [--target /path/to/skills/dir]

set -eu

# ── Configuration ────────────────────────────────────────────────────────────

REPO_URL="https://github.com/linuxdevel/Avalonia-skills"
CANONICAL_DIR="${HOME}/.local/share/avalonia-skills"
SKILL_NAME="avalonia"

# Known agent skills directories (checked in order)
AGENT_DIRS=(
    "${HOME}/.config/opencode/skills"
    "${HOME}/.claude/skills"
    "${HOME}/.agents/skills"
)

# ── Helpers ───────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { printf "${BLUE}  •${RESET} %s\n" "$*"; }
success() { printf "${GREEN}  ✓${RESET} %s\n" "$*"; }
warn()    { printf "${YELLOW}  !${RESET} %s\n" "$*"; }
error()   { printf "${RED}  ✗${RESET} %s\n" "$*" >&2; }
header()  { printf "\n${BOLD}%s${RESET}\n" "$*"; }

# ── Determine install source ──────────────────────────────────────────────────

# If --target is passed, install to that directory instead
EXTRA_TARGET=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            EXTRA_TARGET="$2"
            shift 2
            ;;
        --help|-h)
            printf "Usage: install.sh [--target /path/to/skills/dir]\n"
            printf "  Installs Avalonia skills to all detected agent directories.\n"
            printf "  Physical files go to: %s\n" "${CANONICAL_DIR}"
            printf "  Symlinks are created in each detected agent's skills directory.\n"
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# ── Download / update canonical copy ─────────────────────────────────────────

header "Avalonia Skills Installer"

download_skills() {
    local dest="$1"

    # If we're running from a pipe (curl | sh), we need to download
    # If we're running from the repo directory, we can copy directly
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "")"

    if [[ -n "$script_dir" && -d "$script_dir/skills/avalonia" ]]; then
        info "Using local skills from: $script_dir/skills/avalonia"
        rm -rf "${dest}/skills"
        mkdir -p "${dest}/skills"
        cp -r "$script_dir/skills/avalonia" "${dest}/skills/${SKILL_NAME}"
    elif command -v git &>/dev/null; then
        if [[ -d "${dest}/.git" ]]; then
            info "Updating existing git clone..."
            git -C "${dest}" pull --ff-only
        else
            info "Cloning from ${REPO_URL}..."
            rm -rf "${dest}"
            git clone --depth=1 "${REPO_URL}" "${dest}"
        fi
    elif command -v curl &>/dev/null; then
        info "Downloading archive from ${REPO_URL}..."
        local tmp
        tmp="$(mktemp -d)"
        curl -LsSf "${REPO_URL}/archive/refs/heads/main.tar.gz" -o "${tmp}/avalonia-skills.tar.gz"
        tar -xzf "${tmp}/avalonia-skills.tar.gz" -C "${tmp}"
        rm -rf "${dest}"
        mv "${tmp}/Avalonia-Skills-main" "${dest}"
        rm -rf "${tmp}"
    else
        error "Neither git nor curl is available. Please install git or curl."
        exit 1
    fi
}

mkdir -p "${CANONICAL_DIR}"
download_skills "${CANONICAL_DIR}"
success "Skills downloaded to: ${CANONICAL_DIR}"

SKILLS_SOURCE="${CANONICAL_DIR}/skills/${SKILL_NAME}"
if [[ ! -d "${SKILLS_SOURCE}" ]]; then
    error "Skills source directory not found: ${SKILLS_SOURCE}"
    exit 1
fi

# ── Find agent directories ────────────────────────────────────────────────────

header "Detecting agent skills directories"

FOUND_DIRS=()

for dir in "${AGENT_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        FOUND_DIRS+=("$dir")
        info "Found: $dir"
    fi
done

if [[ -n "${EXTRA_TARGET}" ]]; then
    mkdir -p "${EXTRA_TARGET}"
    FOUND_DIRS+=("${EXTRA_TARGET}")
    info "Added custom target: ${EXTRA_TARGET}"
fi

if [[ ${#FOUND_DIRS[@]} -eq 0 ]]; then
    warn "No agent skills directories detected on this system."
    warn "Tried: ${AGENT_DIRS[*]}"
    warn "Use --target /path/to/skills to specify a directory manually."
    warn "Physical files are available at: ${CANONICAL_DIR}/skills/${SKILL_NAME}"
    exit 0
fi

# ── Install (symlink or copy) into each agent dir ────────────────────────────

header "Installing skills"

install_count=0
skip_count=0

for agent_dir in "${FOUND_DIRS[@]}"; do
    link="${agent_dir}/${SKILL_NAME}"

    if [[ -L "$link" ]]; then
        # Already a symlink — update it
        current_target="$(readlink "$link")"
        if [[ "$current_target" == "$SKILLS_SOURCE" ]]; then
            info "Already up to date: $link"
            ((skip_count++)) || true
            continue
        else
            info "Updating symlink: $link"
            ln -sfn "${SKILLS_SOURCE}" "${link}"
        fi
    elif [[ -d "$link" && ! -L "$link" ]]; then
        # Real directory exists — back it up
        backup="${link}.backup.$(date +%Y%m%d%H%M%S)"
        warn "Directory exists at $link — backing up to $backup"
        mv "$link" "$backup"
        ln -sfn "${SKILLS_SOURCE}" "${link}"
    else
        ln -sfn "${SKILLS_SOURCE}" "${link}"
    fi

    success "Installed: $link -> ${SKILLS_SOURCE}"
    ((install_count++)) || true
done

# ── Summary ───────────────────────────────────────────────────────────────────

header "Done"

printf "\n"
printf "  ${BOLD}Skills installed:${RESET}  %d location(s)\n" "$install_count"
if [[ $skip_count -gt 0 ]]; then
    printf "  ${BOLD}Already current:${RESET}   %d location(s)\n" "$skip_count"
fi
printf "  ${BOLD}Physical files:${RESET}    %s\n" "${CANONICAL_DIR}"
printf "\n"
printf "  ${BOLD}Skills available:${RESET}\n"
printf "    avalonia                 — master router\n"
printf "    avalonia-xaml            — XAML markup and code-behind\n"
printf "    avalonia-layout          — panels and layout\n"
printf "    avalonia-styling         — styles, themes, selectors\n"
printf "    avalonia-data-binding    — bindings and converters\n"
printf "    avalonia-data-templates  — DataTemplate patterns\n"
printf "    avalonia-mvvm            — MVVM pattern\n"
printf "    avalonia-controls        — built-in controls (routes to sub-skills)\n"
printf "    avalonia-custom-controls — UserControl, TemplatedControl\n"
printf "    avalonia-graphics-animation — brushes, transforms, animations\n"
printf "    avalonia-input-interaction  — pointer, keyboard, gestures\n"
printf "    avalonia-property-system    — StyledProperty, DirectProperty\n"
printf "    avalonia-events             — routed events\n"
printf "    avalonia-services           — clipboard, dialogs, notifications\n"
printf "    avalonia-app-development    — app structure and lifetimes\n"
printf "    avalonia-testing            — headless and unit testing\n"
printf "    avalonia-deployment         — packaging for all platforms\n"
printf "    avalonia-wpf-migration      — WPF to Avalonia migration guide\n"
printf "\n"
printf "  To update skills later, re-run this installer.\n"
printf "\n"
