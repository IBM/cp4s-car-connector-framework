#!/bin/bash


LOG_PREFIX=`basename "$0"`

function log()
{
    printf "\e[32m[admin] \e[33m[#{request_id}] \e[35m[#{current_user.login}]\e[0m"
    printf "\x1b[38;2;255;100;0m$(date -u) [$LOG_PREFIX]: $1\x1b[0m\n"
    echo -e "\e[92m $(date -u) [$LOG_PREFIX]: $1"
}

log "START PUBLISHING"

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi


# get branch
if [ -z "$TRAVIS_PULL_REQUEST_BRANCH" ]; then
    EFFECTIVE_BRANCH="${TRAVIS_BRANCH}"
else
    EFFECTIVE_BRANCH="${TRAVIS_PULL_REQUEST_BRANCH}"
fi

# choose repository
if [[ "${EFFECTIVE_BRANCH}" =~ ^(master|develop)$ ]]; then
    PYPI_API_REPOSITORY="${PYPI_API_REPOSITORY_PROD}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_PROD}"
else
    PYPI_API_REPOSITORY="${PYPI_API_REPOSITORY_TEST}"
    PYPI_API_TOKEN="${PYPI_API_TOKEN_TEST}"
fi

# export version
VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)

if [ -z "$TRAVIS_TAG" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${TRAVIS_BUILD_NUMBER}
else 
    export PYPI_PACKAGE_VERSION=${TRAVIS_TAG}
fi


if [ "${TO_PUBLISH}" == "true" ] ; then
    log "TO_PUBLISH is true"

    pip install setuptools wheel twine

    rm -R -f ./build ./dist ./*.egg-info

    python setup.py sdist bdist_wheel

    log "${PYPI_API_TOKEN}" 
    log "${PYPI_API_REPOSITORY}"

    python -m twine upload -u "__token__" -p "${PYPI_API_TOKEN}" --repository-url "${PYPI_API_REPOSITORY}" dist/*
fi