echo "Publishing:"
date -u


VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi

function log()
{
   echo $(date -u) "[$LOG_PREFIX]: $1"
}

if [ -z "$TRAVIS_TAG" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${TRAVIS_BUILD_NUMBER}
else 
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}
fi

echo "PYPI_PACKAGE_VERSION: ${PYPI_PACKAGE_VERSION}"

if [ "${TO_PUBLISH}" == "true" ] ; then
    echo "TO_PUBLISH is true"
fi