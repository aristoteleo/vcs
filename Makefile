.PHONY: list-packages test-env test

CONDA_CHANNELS = -c conda-forge/label/vtk_dev -c cdat/label/vtk_dev -c cdat/label/nightly -c conda-forge

TEST_PACKAGES = vcs
TEST_DEPENDENCIES = udunits2 testsrunner matplotlib image-compare nbformat ipywidgets pytest $(EXTRA_TEST_DEPENDENCIES)

list-packages:
	conda list | grep -E "^(vcs|vtk|mesalib)"

test-env:
	conda create -n test_vcs $(CONDA_CHANNELS) $(TEST_DEPENDENCIES) $(TEST_PACKAGES)

test:
	python run_tests.py -n 4 -H -v2 --timeout=100000 --checkout-baseline --no-vtk-ui
