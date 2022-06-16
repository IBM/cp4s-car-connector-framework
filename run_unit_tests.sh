set -e
set -o pipefail

echo "CURRENT DIRECTORY"
pwd

echo "Installing Dependencies..."
pip install -r requirements-dev.txt

echo "Running Unit Tests..."

python -m pytest -s