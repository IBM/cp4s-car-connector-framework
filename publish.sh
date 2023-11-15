#!/bin/bash


LOG_PREFIX=`basename "$0"`

function log()
{
    echo -e "\e[32m$(date -u) [$LOG_PREFIX]: $1\e[0m"
}

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi

# choose repository
if [[ "${EFFECTIVE_BRANCH}" =~ ^(develop|master|prod-test-.*|v[0-9]+(\.[0-9]+){2,4})$ ]]; then
    # Push to production repo if branch is develop, master, prod-test-* or tag
    PYPI_API_REPOSITORY="${PYPI_API_REPOSITORY_PROD}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_PROD}"
    export PYPI_PACKAGE_REPOSITORY="prod"
else
    PYPI_API_REPOSITORY="${PYPI_API_REPOSITORY_TEST}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_TEST}"
    export PYPI_PACKAGE_REPOSITORY="test"
fi

# Evaluating release tags
if [[ "${EFFECTIVE_BRANCH}" =~ ^(v[0-9]+(\.[0-9]+){2,4})$ ]]; then
    # Pypi tagged as official release
    export PYPI_PACKAGE_VERSION=${EFFECTIVE_BRANCH}
else
    # Pypi tagged as release candidate
    git fetch --prune --unshallow --tags
    VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${RUN_NUMBER}
fi

log "EFFECTIVE_BRANCH: ${EFFECTIVE_BRANCH}"
log "PYPI_PACKAGE_REPOSITORY: ${PYPI_PACKAGE_REPOSITORY}"


if [ "${TO_PUBLISH}" == "true" ] ; then
    log "START PUBLISHING"

    pip install setuptools wheel twine keyring==21.4.0

    rm -R -f ./build ./dist ./*.egg-info

    log "Running setup.py"
    python setup.py sdist bdist_wheel

    log "Uploading Pypi"
    python -m twine upload -u "__token__" -p "${PYPI_API_TOKEN}" --repository-url "${PYPI_API_REPOSITORY}" dist/*
fi