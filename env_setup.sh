#!/bin/bash

VENV_DIR=".venv"
ACTIVATE_SCRIPT="${VENV_DIR}/bin/activate"

packages=(
    docopt
    pyyaml
    requests
    prompter
)

usage() {
    echo "Type this in your shell:"
    echo "  source ${ACTIVATE_SCRIPT}"
}

if [ -d "${VENV_DIR}" ]; then
    echo "Env already set up."
    usage
    exit 0
fi

pyvenv ${VENV_DIR}
source ${ACTIVATE_SCRIPT}

for pkg in ${packages[@]}; do
    pip install ${pkg}
done

usage
