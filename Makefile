.PHONY: list-packages clean-test-env test-env test build

SHELL = /bin/bash

VERSION = 8.2

CONDA = $(patsubst %/bin/conda,%,$(shell find $(HOME)/*conda*/bin -type f -iname conda))
CONDA_CHANNELS = -c conda-forge/label/vtk_dev -c cdat/label/vtk_dev -c cdat/label/nightly -c conda-forge

TEST_PACKAGES = vcs
TEST_DEPENDENCIES = udunits2 testsrunner matplotlib image-compare nbformat ipywidgets pytest $(EXTRA_TEST_DEPENDENCIES)

BUILD = 0
BUILD_DEPENDENCIES = conda-forge-ci-setup=3 pip conda-build anaconda-client conda-smithy conda-verify conda-forge-pinning conda-forge-build-setup conda-forge-ci-setup
BUILD_BRANCH = master

list-packages:
	conda list | grep -E "^(vcs|vtk|mesalib)"

clean-test-env:
	conda env remove -n test_vcs

test-env: clean-test-env
	conda create -n test_vcs $(CONDA_CHANNELS) $(CONDA_EXTRA) $(TEST_DEPENDENCIES) $(TEST_PACKAGES)

debug-env: clean-test-env
	conda create -n test_vcs -c file:///$(CONDA)/envs/build_vcs/conda-bld/ $(CONDA_CHANNELS) $(CONDA_EXTRA) $(TEST_DEPENDENCIES) $(TEST_PACKAGES)

test:
	python run_tests.py -n 4 -H -v2 --timeout=100000 --checkout-baseline --no-vtk-ui

clean-build-env:
	conda env remove -n build_vcs

clean-build: clean-build-env
	rm -rf feedstock/

setup-build: RECIPE_SRC=recipe/meta.yaml.in
setup-build: RECIPE_DST=feedstock/recipe/meta.yaml
setup-build:
	mkdir -p feedstock/recipe

	cp $(RECIPE_SRC) $(RECIPE_DST)

	sed -i.bak "s/@UVCDAT_BRANCH@/$(BUILD_BRANCH)/g" $(RECIPE_DST)
	sed -i.bak "s/@BUILD_NUMBER@/$(BUILD)/g" $(RECIPE_DST)
	sed -i.bak "s/@VERSION@/$(VERSION)/g" $(RECIPE_DST)
	sed -i.bak "s/git:\/\//https:\/\//g" $(RECIPE_DST)

build: clean-build setup-build
	conda create -n build_vcs -c conda-forge $(BUILD_DEPENDENCIES)

	source $(CONDA)/bin/activate build_vcs; \
		echo "recipe_dir: recipe" >> feedstock/conda-forge.yml; \
		conda smithy rerender --feedstock_directory=feedstock/; \
		conda build $(CONDA_CHANNELS) -m feedstock/.ci_support/linux_.yaml --clobber feedstock/.ci_support/linux_.yaml feedstock/recipe/

	git reset HEAD
