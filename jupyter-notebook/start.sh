#!/bin/bash

# Strict mode
set -euo pipefail
IFS=$'\n\t'

# Set configuration defaults
: ${PASSWORD:=""}
: ${PEM_FILE:="/key.pem"}

# Create the hash to pass to the IPython notebook, but don't export it so it doesn't appear
# as an environment variable within IPython kernels themselves
HASH=$(python3 -c "from IPython.lib import passwd; print(passwd('${PASSWORD}'))")
unset PASSWORD

jupyter notebook --no-browser --port 8888 --ip=* --certfile=$PEM_FILE --NotebookApp.password="$HASH"
unset HASH