#!/bin/bash
rm -rf ./dist
rm -rf ./research_task.egg-info
python setup.py sdist
twine check dist/*
twine upload --repository pypi dist/*
