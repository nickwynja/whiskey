prep:
	python3 -m pip install --user --upgrade setuptools wheel twine readme_renderer

pack:
	rm -rf dist/*
	python3 setup.py sdist bdist_wheel

check: pack
	twine check dist/*
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

dist: pack
	python3 -m twine upload dist/*

lint:
	flake8 whiskey
