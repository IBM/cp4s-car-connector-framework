#!/bin/bash


LOG_PREFIX=`basename "$0"`

function log()
{
    echo -e "\e[32m$(date -u) [$LOG_PREFIX]: $1\e[0m"
}

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi


# get branch
if [ -z "${{ github.base_ref }}" ]; then
    EFFECTIVE_BRANCH="${{ github.ref }}"
else
    EFFECTIVE_BRANCH="${{ github.base_ref }}"
fi

# choose repository
if [[ "${EFFECTIVE_BRANCH}" =~ ^(develop|master|prod-test-.*|v[0-9]+(\.[0-9]+){0,4})$ ]]; then
    PYPI_API_REPOSITORY="${vars.PYPI_API_REPOSITORY_PROD}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_PROD}"
    export PYPI_PACKAGE_REPOSITORY="prod"
else
    PYPI_API_REPOSITORY="${PYPI_API_REPOSITORY_PROD}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_PROD}"
    export PYPI_PACKAGE_REPOSITORY="test"
fi

# export version
VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)
log "Version tag: $VERSION_LAST_TAG"
log "Run id: ${{ github.run_id }}"

if [ -z "${{ github.ref }}" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${github.run_id}
else 
    export PYPI_PACKAGE_VERSION=${github.ref}
fi

log "EFFECTIVE_BRANCH: ${EFFECTIVE_BRANCH}"
log "PYPI_PACKAGE_REPOSITORY: ${PYPI_PACKAGE_REPOSITORY}"


if [ "${TO_PUBLISH}" == "true" ] ; then
    log "START PUBLISHING"

    pip install setuptools wheel twine keyring==21.4.0

    rm -R -f ./build ./dist ./*.egg-info

    log "Running setup.py"
    python setup.py sdist bdist_wheel

    echo "Token: $PYPI_API_TOKEN"
    echo "Repo: $PYPI_API_REPOSITORY"

    python -m twine upload -u "__token__" -p "${PYPI_API_TOKEN}" --repository-url "${PYPI_API_REPOSITORY}" dist/*
fi