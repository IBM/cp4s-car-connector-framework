function log()
{
   echo $(date -u) "[$LOG_PREFIX]: $1"
}

echo "Publishing:"
date -u


VERSION_LAST_TAG=$(git describe --abbrev=0 --tags 2>/dev/null)

if [ -z "${TO_PUBLISH}" ]; then
    TO_PUBLISH="true"
fi

if [ -z "$TRAVIS_TAG" ]; then
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}-rc.${TRAVIS_BUILD_NUMBER}
else 
    export PYPI_PACKAGE_VERSION=${VERSION_LAST_TAG}
fi

echo "TRAVIS_TAG: ${TRAVIS_TAG}"
echo "PYPI_PACKAGE_VERSION: ${PYPI_PACKAGE_VERSION}"

if [ "${TO_PUBLISH}" == "true" ] ; then
    echo "TO_PUBLISH is true"

    pip install setuptools wheel twine

    rm -R -f ./build ./dist ./*.egg-info

    python setup.py sdist bdist_wheel

    # python3 -m twine upload -u "__token__" -p "<TOKEN>" --repository testpypi dist/*

fi