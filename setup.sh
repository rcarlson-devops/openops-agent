#!/usr/bin/env bash

# ==============================================================================
# OpenOps-Agent Initialization & Environment Bootstrap Script
# ==============================================================================
# Sets up directory trees, stubs source paths, initializes python environments,
# and verifies local network connections for the AI platform stack.
# ==============================================================================

set -euo pipefail

# Text color definitions for status formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "Starting OpenOps-Agent platform bootstrap..."

# ------------------------------------------------------------------------------
# Step 1: Verify System Dependencies
# ------------------------------------------------------------------------------
log_info "Verifying core workspace binaries..."

for cmd in python3 pip3 git npm; do
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Missing required system dependency: $cmd. Please install it before re-running."
        exit 1
    fi
done
log_info "All prerequisite system binaries found."

# ------------------------------------------------------------------------------
# Step 2: Stub Out Modular Directory Layout
# ------------------------------------------------------------------------------
log_info "Constructing modular repository directory tree..."

mkdir -p src data/profile data/jobs data/interview-questions tests

# Generate empty placeholder files if they do not exist
touch src/__init__.py
touch src/agent.py
touch src/ingest.py
touch src/mcp_server.py
touch data/profile/.gitkeep
touch data/jobs/.gitkeep
touch data/interview-questions/.gitkeep
touch tests/promptfooconfig.yaml

log_info "Directory layouts and python modules successfully stubbed."

# ------------------------------------------------------------------------------
# Step 3: Initialize Python Virtual Environment (.venv)
# ------------------------------------------------------------------------------
log_info "Initializing sandboxed Python 3 virtual environment..."

if [ -d ".venv" ]; then
    log_warn "Existing .venv directory found. Skipping environment creation."
else
    python3 -m venv .venv
    log_info "Virtual environment successfully generated at ./.venv"
fi

# Ensure all python actions happen inside the virtual environment boundary
VENV_BIN="./.venv/bin"
if [ ! -f "$VENV_BIN/activate" ]; then
    log_error "Could not locate virtual environment binary directory. Exiting."
    exit 1
fi

# Upgrade pip inside the environment
log_info "Upgrading pip package manager..."
"$VENV_BIN/pip" install --upgrade pip

# ------------------------------------------------------------------------------
# Step 4: Write out exact requirements.txt file
# ------------------------------------------------------------------------------
log_info "Writing python dependency manifest (requirements.txt)..."

cat << 'EOF' > requirements.txt
# Core LangChain & LangGraph Orchestration Stack
langchain-core==1.6.12
langchain-ollama==1.1.0
langchain-chroma==1.1.0
langgraph==1.2.16

# Official Anthropic Model Context Protocol SDK
mcp==1.1.2

# Configuration, Utilities, & System Interfaces
python-dotenv==1.2.4
pydantic==2.9.2
EOF

# Install python components
log_info "Executing python package installations inside the virtual environment..."
"$VENV_BIN/pip" install -r requirements.txt
log_info "Python dependencies successfully installed."

# ------------------------------------------------------------------------------
# Step 5: Generate Local Environment Configuration Templates
# ------------------------------------------------------------------------------
log_info "Configuring localized network environment templates (.env.example)..."

cat << 'EOF' > .env.example
# ==============================================================================
# OpenOps-Agent Network Interface Properties Template
# ==============================================================================
# For WSL2 Ubuntu execution loops, update this variable to match your Windows
# Host Ethernet Adapter vEthernet IP bridge (e.g., http://172.29.96.1:11434).
# ==============================================================================
OLLAMA_BASE_URL="http://localhost:11434"
EOF

if [ ! -f ".env" ]; then
    cp .env.example .env
    log_warn "Generated default runtime environment file (.env). Please modify it to match your network path if running in WSL2."
else
    log_info "Active .env configuration file detected. Skipping template override."
fi

# ------------------------------------------------------------------------------
# Step 6: Verify global promptfoo installation
# ------------------------------------------------------------------------------
log_info "Verifying promptfoo CI/CD validation installation..."

if ! command -v promptfoo &> /dev/null; then
    log_warn "promptfoo is not installed globally in your system path."
    log_warn "To install it for testing execution arrays, run: npm install -g promptfoo --allow-scripts=esbuild"
else
    log_info "promptfoo testing binary verified: $(promptfoo --version)"
fi

# ------------------------------------------------------------------------------
# Bootstrap Verification Summary
# ------------------------------------------------------------------------------
echo -e "\n=============================================================================="
log_info "OpenOps-Agent Local Platform Bootstrap Complete!"
echo -e "=============================================================================="
echo -e " To activate your python runtime environment, run:"
echo -e "   ${GREEN}source .venv/bin/activate${NC}"
echo -e ""
echo -e " Next Implementation Step: Populate your 'runbooks/runbook-101.md' file"
echo -e " and build out your modular 'src/' components."
echo -e "==============================================================================\n"