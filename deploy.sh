#!/bin/bash
rm -rf ./dist
rm -rf ./wormcat_batch.egg-info
python setup.py sdist
twine check dist/*
twine upload --repository pypi dist/*
