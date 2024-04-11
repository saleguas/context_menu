del build /Q
del context_menu.egg-info /Q
del dist /Q
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://upload.pypi.org/legacy/ -u __token__ -p your_token_here dist/*