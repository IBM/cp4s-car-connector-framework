set -e
set -o pipefail


echo "CURRENT DIRECTORY"
pwd


# echo "Installing Dev environment"
# export ARTIFACTORY_USER_ENCODED=$(echo $ARTIFACTORY_USER | sed 's/@/%40/')
# export PIP_INDEX_URL=https://${ARTIFACTORY_USER_ENCODED}:${ARTIFACTORY_API}@na.artifactory.swg-devops.com/artifactory/api/pypi/sec-uds-pypi-virtual/simple
# echo "PIP_INDEX_URL is ${PIP_INDEX_URL}"


echo "Installing Dependencies..."
pip install -r requirements-dev.txt

# ./scripts/devops/python/install-dev-env.sh
# virtualenv -p python3.6 --no-site-packages --distribute virtualenv && source virtualenv/bin/activate && pip install -r requirements-dev.txt
# ls -a
# source virtualenv/bin/activate

echo "Running Unit Tests..."

python -m pytest -s