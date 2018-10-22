# q2-sample-classifier

[![Build Status](https://travis-ci.org/qiime2/q2-sample-classifier.svg?branch=master)](https://travis-ci.org/qiime2/q2-sample-classifier) [![Coverage Status](https://coveralls.io/repos/github/qiime2/q2-sample-classifier/badge.svg?branch=master)](https://coveralls.io/github/qiime2/q2-sample-classifier?branch=master) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1468879.svg)](https://doi.org/10.5281/zenodo.1468879) [![status](http://joss.theoj.org/papers/d828a4ecf73eb6a147f8634e9054eeee/status.svg)](http://joss.theoj.org/papers/d828a4ecf73eb6a147f8634e9054eeee)


QIIME 2 plugin for machine learning prediction of sample data.

Microbiome studies often aim to predict outcomes or differentiate samples based on their microbial compositions, tasks that can be efficiently performed by supervised learning methods. The q2-sample-classifier plugin makes these methods more accessible, reproducible, and interpretable to a broad audience of microbiologists, clinicians, and others who wish to utilize supervised learning methods for predicting sample characteristics based on microbiome composition or other "omics" data.

## Installation

Follow the QIIME 2 core distribution installation instructions at https://qiime2.org/ to install q2-sample-classifier as part of the QIIME 2 analysis platform.

To test deployment, run:
```
pytest --disable-pytest-warnings --pyargs q2_sample_classifier
```

## Example usage

This is a QIIME 2 plugin. For details on QIIME 2 and tutorials demonstrating how to use this plugin, see the [QIIME 2 documentation](https://qiime2.org/). Tutorials for this plugin can be found [here](https://docs.qiime2.org/2018.8/tutorials/sample-classifier/).

Not sure which learning model to use? A good starting point is [this flowchart](http://scikit-learn.org/dev/tutorial/machine_learning_map/index.html). Most of the classification and regression models shown in that chart (and a few extras) are implemented in q2-sample-classifier.

## API documentation

API documentation can be found [here](https://docs.qiime2.org/2018.8/plugins/available/sample-classifier/).

## Help

For user support, see the [QIIME 2 Forum](https://forum.qiime2.org). Bug reports and feature requests can also be made [via a new issue](https://github.com/qiime2/q2-sample-classifier/issues/new/choose).

## Contributing

QIIME 2 is an open-source project, and we are very interested in contributions from the community. Please see the [contributing guidelines](https://github.com/qiime2/q2-sample-classifier/blob/master/.github/CONTRIBUTING.md) if you would like to get involved.
