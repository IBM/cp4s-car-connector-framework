## Publish to pypi

https://packaging.python.org/tutorials/packaging-projects/

Change version in setup.py file (increment)
Run the following commands once:
`python3 -m pip install --user --upgrade setuptools wheel`
`python3 -m pip install --user --upgrade twine`
Delete ./build , ./dist and ./*.egg-info folders:
`rm -R ./build ./dist ./*.egg-info`
Run distribution build:
`python3 setup.py sdist bdist_wheel`
Uploading the distribution archives:
`python3 -m twine upload -u "__token__" -p "<TOKEN>" --repository testpypi dist/*`
OR if you have ~/.pypirc setup
`python3 -m twine upload --repository testpypi dist/*`


Test a project using this module by:# 
pip install -i https://test.pypi.org/simple/ car-connector-framework==0.0.11
