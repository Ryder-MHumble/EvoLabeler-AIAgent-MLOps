#!/bin/bash

# =============================================================================
# EvoLabeler Quick-Start Script
# AI-Driven MLOps Engine for Remote Sensing
# =============================================================================

# ---------------------------------------------------------------------------
# ANSI color codes (256-color)
# ---------------------------------------------------------------------------
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"

# Gradient palette: deep cyan -> bright cyan -> light blue -> pale blue
C1="\033[38;5;45m"    # deep cyan
C2="\033[38;5;51m"    # bright cyan
C3="\033[38;5;87m"    # light blue
C4="\033[38;5;123m"   # pale blue

WHITE="\033[38;5;255m"
CYAN="\033[38;5;51m"
BLUE="\033[38;5;75m"
GREEN="\033[38;5;82m"
YELLOW="\033[38;5;220m"
RED="\033[38;5;196m"
GRAY="\033[38;5;244m"
DARK_GRAY="\033[38;5;238m"
ORANGE="\033[38;5;214m"

# Box-drawing border color
BORDER="\033[38;5;32m"

# ---------------------------------------------------------------------------
# Graceful Ctrl+C handler
# ---------------------------------------------------------------------------
trap 'echo -e "\n\n${YELLOW}  Interrupted. Goodbye!${RESET}\n"; exit 0' INT TERM

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

clear_screen() { clear; }

print_banner() {
    echo
    echo -e "${C1} ███████╗${C2}██╗   ██╗${C3} ██████╗ ${RESET}"
    echo -e "${C1} ██╔════╝${C2}██║   ██║${C3}██╔═══██╗${RESET}"
    echo -e "${C1} █████╗  ${C2}██║   ██║${C3}██║   ██║${RESET}"
    echo -e "${C1} ██╔══╝  ${C2}╚██╗ ██╔╝${C3}██║   ██║${RESET}"
    echo -e "${C1} ███████╗${C2} ╚████╔╝ ${C3}╚██████╔╝${RESET}"
    echo -e "${C1} ╚══════╝${C2}  ╚═══╝  ${C3} ╚═════╝ ${RESET}"
    echo
    echo -e "  ${C4}${BOLD}L A B E L E R${RESET}   ${DIM}${GRAY}AI-Driven MLOps Engine for Remote Sensing${RESET}"
    echo
}

print_info_box() {
    echo -e " ${BORDER}┌─────────────────────────────────────────────────────────┐${RESET}"
    echo -e " ${BORDER}│${RESET}  ${DIM}Version:${RESET} ${WHITE}v1.1.0-dev${RESET}    ${DIM}Stack:${RESET} ${WHITE}Vue3 + Electron + Vite${RESET}   ${BORDER}│${RESET}"
    echo -e " ${BORDER}│${RESET}  ${DIM}Frontend:${RESET} ${CYAN}http://localhost:5173${RESET}    ${DIM}Backend:${RESET} ${CYAN}:8000${RESET}       ${BORDER}│${RESET}"
    echo -e " ${BORDER}└─────────────────────────────────────────────────────────┘${RESET}"
    echo
}

print_divider() {
    echo -e " ${DARK_GRAY}─────────────────────────────────────────────────────────────${RESET}"
}

print_menu() {
    print_divider
    echo -e "  ${DIM}${GRAY}Select an option:${RESET}"
    echo
    # Show electron status badge next to electron options
    if electron_ok; then
        E_BADGE="${GREEN}●${RESET}"
    else
        E_BADGE="${RED}●${RESET}"
    fi
    echo -e "  ${CYAN}${BOLD}[1]${RESET}  ${WHITE}Web Preview Mode${RESET}              ${DIM}${GRAY}Browser only · http://localhost:5173${RESET}"
    echo -e "  ${CYAN}${BOLD}[2]${RESET}  ${WHITE}Electron Dev Mode${RESET}  ${E_BADGE}         ${DIM}${GRAY}Desktop app · hot-reload${RESET}"
    echo -e "  ${CYAN}${BOLD}[3]${RESET}  ${WHITE}Install / Repair Dependencies${RESET} ${DIM}${GRAY}npm install + fix Electron binary${RESET}"
    echo -e "  ${CYAN}${BOLD}[4]${RESET}  ${WHITE}Build for macOS${RESET}               ${DIM}${GRAY}Outputs .dmg (x64 + arm64)${RESET}"
    echo -e "  ${CYAN}${BOLD}[5]${RESET}  ${WHITE}Build for Windows${RESET}             ${DIM}${GRAY}Outputs NSIS installer (x64)${RESET}"
    echo -e "  ${CYAN}${BOLD}[6]${RESET}  ${WHITE}Show Project Info${RESET}             ${DIM}${GRAY}Environment + dependency status${RESET}"
    echo -e "  ${CYAN}${BOLD}[7]${RESET}  ${WHITE}Exit${RESET}"
    echo
    print_divider
    echo
    printf "  ${CYAN}${BOLD}>${RESET} "
}

press_any_key() {
    echo
    echo -e "  ${DIM}${GRAY}Press any key to return to the menu...${RESET}"
    read -r -s -n 1
}

# ---------------------------------------------------------------------------
# Electron health check & repair
# ---------------------------------------------------------------------------

ELECTRON_MODULE_DIR=""

# Find the electron module that vite-plugin-electron will actually use.
# npm workspaces hoists it to the root; fall back to frontend workspace.
_resolve_electron_dir() {
    if [[ -f "${PROJECT_ROOT}/node_modules/electron/index.js" ]]; then
        echo "${PROJECT_ROOT}/node_modules/electron"
    elif [[ -f "${FRONTEND_DIR}/node_modules/electron/index.js" ]]; then
        echo "${FRONTEND_DIR}/node_modules/electron"
    else
        echo ""
    fi
}

electron_ok() {
    local dir
    dir=$(_resolve_electron_dir)
    [[ -n "$dir" ]] && [[ -f "${dir}/path.txt" ]] && [[ -d "${dir}/dist" ]]
}

# Return the path to a fully-installed electron cache (has path.txt + dist/)
_find_electron_cache() {
    # Common locations where npm caches the electron binary during postinstall
    local candidates=(
        "${FRONTEND_DIR}/node_modules/.electron-oZl8v5DK"
        "${FRONTEND_DIR}/node_modules/.cache/electron"
        "${PROJECT_ROOT}/node_modules/.cache/electron"
    )
    for d in "${candidates[@]}"; do
        if [[ -f "${d}/path.txt" ]] && [[ -d "${d}/dist" ]]; then
            echo "$d"
            return 0
        fi
    done
    # Search any .electron-* hidden dir inside frontend node_modules
    local found
    found=$(find "${FRONTEND_DIR}/node_modules" -maxdepth 1 -name '.electron-*' \
            -type d 2>/dev/null | head -1)
    if [[ -n "$found" ]] && [[ -f "${found}/path.txt" ]] && [[ -d "${found}/dist" ]]; then
        echo "$found"
        return 0
    fi
    echo ""
    return 1
}

repair_electron() {
    local dir
    dir=$(_resolve_electron_dir)

    if [[ -z "$dir" ]]; then
        echo -e "  ${RED}✘  Electron module not found. Run option 3 first.${RESET}"
        return 1
    fi

    # Already healthy
    if [[ -f "${dir}/path.txt" ]] && [[ -d "${dir}/dist" ]]; then
        echo -e "  ${GREEN}✔  Electron binary already healthy.${RESET}"
        return 0
    fi

    echo -e "  ${YELLOW}⚠  Electron binary missing — attempting repair...${RESET}"

    # Try to use an existing cache first (fast, offline)
    local cache
    cache=$(_find_electron_cache)
    if [[ -n "$cache" ]]; then
        cp "${cache}/path.txt" "${dir}/path.txt" 2>/dev/null
        # Symlink dist to avoid duplicating the ~200 MB binary
        rm -rf "${dir}/dist" 2>/dev/null
        ln -sf "${cache}/dist" "${dir}/dist"
        if [[ -f "${dir}/path.txt" ]] && [[ -d "${dir}/dist" ]]; then
            echo -e "  ${GREEN}✔  Repaired from local cache: ${GRAY}${cache}${RESET}"
            return 0
        fi
    fi

    # Cache not available — re-run the postinstall script (downloads binary)
    echo -e "  ${DIM}${GRAY}Downloading Electron binary (this may take a moment)...${RESET}"
    pushd "$dir" > /dev/null
    ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" \
    ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/" \
        node install.js 2>&1 | sed 's/^/    /'
    local rc=$?
    popd > /dev/null

    if [[ $rc -eq 0 ]] && [[ -f "${dir}/path.txt" ]]; then
        echo -e "  ${GREEN}✔  Electron binary downloaded successfully.${RESET}"
        return 0
    else
        echo -e "  ${RED}✘  Could not repair Electron binary automatically.${RESET}"
        echo -e "  ${GRAY}Try manually: ${CYAN}cd ${dir} && node install.js${RESET}"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Resolve project root
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"

check_dir() {
    if [[ ! -d "${PROJECT_ROOT}/evolauncher-frontend" ]]; then
        echo -e "\n  ${RED}${BOLD}Error:${RESET} ${WHITE}Cannot find 'evolauncher-frontend' directory.${RESET}"
        echo -e "  ${GRAY}Expected root: ${YELLOW}${PROJECT_ROOT}${RESET}"
        echo -e "  ${GRAY}Please run this script from the EvoLabeler project root.${RESET}\n"
        exit 1
    fi
}

check_dir
FRONTEND_DIR="${PROJECT_ROOT}/evolauncher-frontend"

# ---------------------------------------------------------------------------
# Environment info
# ---------------------------------------------------------------------------

check_env() {
    echo
    echo -e "  ${CYAN}${BOLD}Environment Check${RESET}"
    print_divider

    if command -v node &>/dev/null; then
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}Node.js${RESET}        ${GRAY}$(node --version)${RESET}"
    else
        echo -e "  ${RED}✘${RESET}  ${WHITE}Node.js${RESET}        ${RED}not found — https://nodejs.org${RESET}"
    fi

    if command -v npm &>/dev/null; then
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}npm${RESET}            ${GRAY}v$(npm --version)${RESET}"
    else
        echo -e "  ${RED}✘${RESET}  ${WHITE}npm${RESET}            ${RED}not found${RESET}"
    fi

    if command -v python3 &>/dev/null; then
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}Python${RESET}         ${GRAY}$(python3 --version 2>&1)${RESET}"
    elif command -v python &>/dev/null; then
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}Python${RESET}         ${GRAY}$(python --version 2>&1)${RESET}"
    else
        echo -e "  ${YELLOW}!${RESET}  ${WHITE}Python${RESET}         ${YELLOW}not found (required for FastAPI backend)${RESET}"
    fi

    if electron_ok; then
        local edir
        edir=$(_resolve_electron_dir)
        local ever
        ever=$(cat "${edir}/dist/version" 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}Electron${RESET}       ${GRAY}v${ever}${RESET}"
    else
        echo -e "  ${RED}✘${RESET}  ${WHITE}Electron${RESET}       ${RED}binary missing — run option 3 to repair${RESET}"
    fi

    if [[ -d "${FRONTEND_DIR}/node_modules" ]]; then
        local count
        count=$(ls "${FRONTEND_DIR}/node_modules" | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✔${RESET}  ${WHITE}node_modules${RESET}   ${GRAY}${count} packages${RESET}"
    else
        echo -e "  ${RED}✘${RESET}  ${WHITE}node_modules${RESET}   ${RED}not installed — run option 3${RESET}"
    fi

    print_divider
}

show_project_info() {
    echo
    echo -e "  ${C2}${BOLD}EvoLabeler — Project Information${RESET}"
    print_divider
    echo -e "  ${DIM}Root:${RESET}          ${YELLOW}${PROJECT_ROOT}${RESET}"
    echo -e "  ${DIM}Frontend:${RESET}      ${YELLOW}${FRONTEND_DIR}${RESET}"
    echo -e "  ${DIM}Backend:${RESET}       ${YELLOW}${PROJECT_ROOT}/backend${RESET}"
    echo -e "  ${DIM}Stack:${RESET}         ${WHITE}Vue 3 · Electron 28 · Vite 5 · TypeScript${RESET}"
    echo -e "  ${DIM}Dev port:${RESET}      ${CYAN}5173${RESET}"
    echo -e "  ${DIM}API port:${RESET}      ${CYAN}8000${RESET}"
    echo -e "  ${DIM}Version:${RESET}       ${WHITE}v1.1.0-dev${RESET}"
    print_divider
    check_env
}

# ---------------------------------------------------------------------------
# Option handlers
# ---------------------------------------------------------------------------

option_web_preview() {
    echo
    echo -e "  ${GREEN}${BOLD}Starting Web Preview Mode...${RESET}"
    echo -e "  ${GRAY}Electron will NOT launch — open ${CYAN}http://localhost:5173${GRAY} in your browser.${RESET}"
    echo -e "  ${GRAY}Directory: ${YELLOW}${FRONTEND_DIR}${RESET}"
    echo -e "  ${GRAY}Command:   ${CYAN}ELECTRON_SKIP_LAUNCH=1 npm run dev${RESET}"
    print_divider
    echo
    cd "${FRONTEND_DIR}" && ELECTRON_SKIP_LAUNCH=1 npm run dev
}

option_electron_dev() {
    # Guard: repair electron binary if needed before starting
    if ! electron_ok; then
        echo
        echo -e "  ${YELLOW}${BOLD}⚠  Electron binary is not installed.${RESET}"
        repair_electron
        echo
        if ! electron_ok; then
            echo -e "  ${RED}Cannot start Electron dev mode. Fix the binary first.${RESET}"
            return 1
        fi
    fi
    echo
    echo -e "  ${GREEN}${BOLD}Starting Electron Dev Mode...${RESET}"
    echo -e "  ${GRAY}Directory: ${YELLOW}${FRONTEND_DIR}${RESET}"
    echo -e "  ${GRAY}Command:   ${CYAN}npm run electron:dev${RESET}"
    print_divider
    echo
    cd "${FRONTEND_DIR}" && npm run electron:dev
}

option_install() {
    echo
    echo -e "  ${GREEN}${BOLD}Installing / Repairing Dependencies...${RESET}"
    echo -e "  ${GRAY}Directory: ${YELLOW}${FRONTEND_DIR}${RESET}"
    print_divider
    echo

    # Step 1: npm install
    echo -e "  ${CYAN}[1/2]${RESET} Running npm install..."
    cd "${FRONTEND_DIR}" && npm install
    local npm_rc=$?
    echo
    if [[ $npm_rc -eq 0 ]]; then
        echo -e "  ${GREEN}✔  npm install succeeded.${RESET}"
    else
        echo -e "  ${RED}✘  npm install failed (exit ${npm_rc}).${RESET}"
        return 1
    fi

    # Step 2: Verify / repair Electron binary
    echo
    echo -e "  ${CYAN}[2/2]${RESET} Checking Electron binary..."
    repair_electron

    echo
    if electron_ok; then
        echo -e "  ${GREEN}${BOLD}✔  All dependencies ready.${RESET}"
    else
        echo -e "  ${YELLOW}${BOLD}⚠  Dependencies installed but Electron binary still missing.${RESET}"
        echo -e "  ${GRAY}Try running: ${CYAN}cd ${FRONTEND_DIR} && npm install${RESET}"
    fi
}

option_build_mac() {
    if ! electron_ok; then
        echo
        echo -e "  ${YELLOW}${BOLD}⚠  Electron binary missing.${RESET}"
        repair_electron
        echo
        if ! electron_ok; then
            echo -e "  ${RED}Cannot build without Electron binary. Run option 3 first.${RESET}"
            return 1
        fi
    fi
    echo
    echo -e "  ${GREEN}${BOLD}Building for macOS...${RESET}"
    echo -e "  ${GRAY}Directory: ${YELLOW}${FRONTEND_DIR}${RESET}"
    echo -e "  ${GRAY}Command:   ${CYAN}npm run build:mac${RESET}"
    echo -e "  ${GRAY}Output:    ${YELLOW}${FRONTEND_DIR}/release${RESET}"
    print_divider
    echo
    cd "${FRONTEND_DIR}" && npm run build:mac
    local rc=$?
    echo
    if [[ $rc -eq 0 ]]; then
        echo -e "  ${GREEN}${BOLD}✔  macOS build complete.${RESET}"
        echo -e "  ${GRAY}Find your .dmg in: ${YELLOW}${FRONTEND_DIR}/release${RESET}"
    else
        echo -e "  ${RED}${BOLD}✘  Build failed (exit ${rc}).${RESET}"
    fi
}

option_build_win() {
    if ! electron_ok; then
        echo
        echo -e "  ${YELLOW}${BOLD}⚠  Electron binary missing.${RESET}"
        repair_electron
        echo
        if ! electron_ok; then
            echo -e "  ${RED}Cannot build without Electron binary. Run option 3 first.${RESET}"
            return 1
        fi
    fi
    echo
    echo -e "  ${GREEN}${BOLD}Building for Windows...${RESET}"
    echo -e "  ${GRAY}Directory: ${YELLOW}${FRONTEND_DIR}${RESET}"
    echo -e "  ${GRAY}Command:   ${CYAN}npm run build:win${RESET}"
    echo -e "  ${GRAY}Output:    ${YELLOW}${FRONTEND_DIR}/release${RESET}"
    print_divider
    echo
    cd "${FRONTEND_DIR}" && npm run build:win
    local rc=$?
    echo
    if [[ $rc -eq 0 ]]; then
        echo -e "  ${GREEN}${BOLD}✔  Windows build complete.${RESET}"
        echo -e "  ${GRAY}Find your installer in: ${YELLOW}${FRONTEND_DIR}/release${RESET}"
    else
        echo -e "  ${RED}${BOLD}✘  Build failed (exit ${rc}).${RESET}"
    fi
}

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

main() {
    while true; do
        clear_screen
        print_banner
        print_info_box
        print_menu
        read -r choice

        case "$choice" in
            1)
                clear_screen; print_banner
                option_web_preview
                press_any_key
                ;;
            2)
                clear_screen; print_banner
                option_electron_dev
                press_any_key
                ;;
            3)
                clear_screen; print_banner
                option_install
                press_any_key
                ;;
            4)
                clear_screen; print_banner
                option_build_mac
                press_any_key
                ;;
            5)
                clear_screen; print_banner
                option_build_win
                press_any_key
                ;;
            6)
                clear_screen; print_banner
                show_project_info
                press_any_key
                ;;
            7|q|Q|exit|quit)
                clear_screen; print_banner
                echo -e "  ${GRAY}Goodbye! Happy labeling.${RESET}"
                echo
                exit 0
                ;;
            *)
                echo -e "\n  ${RED}Invalid choice:${RESET} ${WHITE}${choice}${RESET}  ${GRAY}(enter 1–7)${RESET}"
                sleep 1
                ;;
        esac
    done
}

main
