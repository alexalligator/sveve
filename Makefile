# In terminal run:
# make release

# Reads version from pyproject.toml
version := $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
current_branch := $(shell git symbolic-ref --short HEAD)

.SILENT: release

release: check_branch changelog build upload git_release clean

check_branch:
	@if [ "$(current_branch)" != "master" ]; then \
		echo "You are not on the master branch. Please switch to the master branch before releasing."; \
		exit 1; \
	fi

changelog:
	scriv collect

build:
	python -m build

upload:
	python -m twine upload dist/* --skip-existing

git_release:
	-git commit -a -m $(version)
	git push
	git tag -a $(version) -m $(version)
	git push origin $(version)
	scriv github-release

clean:
	-rm -r build