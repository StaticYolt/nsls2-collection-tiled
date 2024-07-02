#!/bin/bash

set -euo pipefail

# Usage:
#   $ bash download-artifacts.sh nsls2-collection-tiled 627190580 2023-1.3-py310-tiled

# Example:
#   # https://github.com/nsls2-conda-envs/nsls2-collection-tiled/suites/11958755002/artifacts/627190580
#   repo_name="nsls2-collection-tiled"
#   org_name="StaticYolt"
#   artifact_id="627190580"
#   envname="2023-1.3-py310-tiled"


repo_name=${1:-""}
org_name=${2:-""}
artifact_id=${3:-""}
envname=${4:-""}

if [ -z "${repo_name}" -o -z "${org_name}" -o -z "${artifact_id}" -o -z "${envname}" ]; then
    echo "repo_name (arg #1), org_name (arg #2), artifact_id (arg #3), and envname (arg #4) must be defined".
    exit 1
fi

if [ -z "${GHA_TOKEN}" ]; then
    echo "'GHA_TOKEN' env var must be defined"
    exit 2
fi

echo -e "\nDownloading the artifact_id=${artifact_id} for the '${repo_name}' repo: envname=${envname}\n"

archive_name="${envname}.zip"
#curl -L -H "Authorization: token ${GHA_TOKEN}" "https://api.github.com/repos/nsls2-conda-envs/${repo_name}/actions/artifacts/${artifact_id}/zip" > ${archive_name}
curl -L "https://api.github.com/repos/${org_name}/${repo_name}/actions/artifacts/${artifact_id}/zip" > ${archive_name}
unzip -v ${archive_name}  # contents info
unzip ${archive_name}
# mv -v Dockerfile Dockerfile-${envname}
rm -fv ${archive_name}
