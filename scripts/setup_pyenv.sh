#!/usr/bin/env bash
set -euo pipefail

# Simple helper to set up Python 3.10 via pyenv and install dependencies
PY_VERSION="3.10.12"
VENV_NAME="mediapipe_gesture_recognition"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv not found. Please install pyenv first: https://github.com/pyenv/pyenv#installation"
  exit 1
fi

echo "Using pyenv to ensure Python $PY_VERSION is available..."
pyenv install -s "$PY_VERSION"

# If pyenv-virtualenv is available, create and use a named virtualenv
if pyenv virtualenvs --bare >/dev/null 2>&1; then
  if ! pyenv virtualenvs --bare | grep -qx "$VENV_NAME"; then
    echo "Creating pyenv virtualenv $VENV_NAME..."
    pyenv virtualenv "$PY_VERSION" "$VENV_NAME"
  fi
  echo "Setting local pyenv version to virtualenv $VENV_NAME"
  pyenv local "$VENV_NAME"
else
  echo "pyenv-virtualenv not found; setting local python to $PY_VERSION"
  pyenv local "$PY_VERSION"
fi

PY_BIN="$(pyenv which python)"
echo "Installing pip dependencies into: $PY_BIN"
"$PY_BIN" -m pip install --upgrade pip
"$PY_BIN" -m pip install -r "$REPO_ROOT/requirements.txt"

echo "\nSetup complete. To use the environment:"
echo "  cd $REPO_ROOT"
echo "  pyenv local $VENV_NAME   # or 'pyenv local $PY_VERSION' if no virtualenv created"
echo "  # then run: python demo.py"
