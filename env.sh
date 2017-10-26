#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -n "$MFILEDOWNLOAD" ]; then
    export MFILEDOWNLOAD="${CURRENT_DIR}"
fi

if [ -d "${CURRENT_DIR}/deploy_conf" ]; then
    `cp -r ${CURRENT_DIR}/deploy_conf/* ${CURRENT_DIR}/conf`
fi
mkdir -p ${CURRENT_DIR}/logs
Prog=/home/work/env/python-2.7/bin/python
PATH="/home/work/env/python-2.7/bin/:$HOME/.local/bin:$HOME/bin:$PATH"
export PATH