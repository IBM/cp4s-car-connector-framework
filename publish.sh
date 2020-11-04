function log()
{
   echo $(date -u) "[$LOG_PREFIX]: $1"
}

log "Staring Publish"

VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi

if [ -z "$TRAVIS_TAG" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${TRAVIS_BUILD_NUMBER}
else 
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}
fi

# log "TRAVIS_TAG: ${TRAVIS_TAG}"
# log "TRAVIS_BRANCH: ${TRAVIS_BRANCH}"
# log "PYPI_PACKAGE_VERSION: ${PYPI_PACKAGE_VERSION}"

# PYPI_API_REPOSITORY_PROD
# PYPI_API_REPOSITORY_TEST
# PYPI_API_TOKEN_PROD
# PYPI_API_TOKEN_TEST 


env

if [ -z "$TRAVIS_TAG" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${TRAVIS_BUILD_NUMBER}
else 
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}
fi


if [ "${TO_PUBLISH}" == "true" ] ; then
    log "TO_PUBLISH is true"

    pip install setuptools wheel twine

    rm -R -f ./build ./dist ./*.egg-info

    python setup.py sdist bdist_wheel

    # python3 -m twine upload -u "__token__" -p "${PYPI_API_TOKEN}" --repository testpypi dist/*

fi