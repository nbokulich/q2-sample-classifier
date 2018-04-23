# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (
    Int, Str, Float, Range, Bool, Plugin, Metadata, Choices, MetadataColumn,
    Numeric, Categorical, SemanticType, Citations)
from q2_types.feature_table import FeatureTable, Frequency
from q2_types.sample_data import SampleData
from .classify import (
    classify_samples, regress_samples, maturity_index)
from .visuals import _custom_palettes
import q2_sample_classifier
import qiime2.plugin.model as model
import pandas as pd
import qiime2


citations = Citations.load('citations.bib', package='q2_sample_classifier')

plugin = Plugin(
    name='sample-classifier',
    version=q2_sample_classifier.__version__,
    website="https://github.com/qiime2/q2-sample-classifier",
    package='q2_sample_classifier',
    description=(
        'This QIIME 2 plugin supports methods for supervised classification '
        'and regression of sample metadata, and other supervised machine '
        'learning methods.'),
    short_description=(
        'Plugin for machine learning prediction of sample metadata.'),
    citations=[citations['Bokulich306167']]
)


BooleanSeries = SemanticType(
    'BooleanSeries', variant_of=SampleData.field['type'])


class BooleanSeriesFormat(model.TextFileFormat):
    def sniff(self):
        with self.open() as fh:
            line = fh.readline()
            for line, _ in zip(fh, range(5)):
                cells = line.strip().split('\t')
                if len(cells) != 2 or str(cells[1]) not in ('True', 'False'):
                    return False
            return True


BooleanSeriesDirectoryFormat = model.SingleFileDirectoryFormat(
    'BooleanSeriesDirectoryFormat', 'outliers.tsv',
    BooleanSeriesFormat)


def _read_dataframe(fh):
    # Using `dtype=object` and `set_index` to avoid type casting/inference
    # of any columns or the index.
    df = pd.read_csv(fh, sep='\t', header=0, dtype='str')
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    df.index.name = 'id'
    return df


@plugin.register_transformer
def _4(data: pd.Series) -> (BooleanSeriesFormat):
    ff = BooleanSeriesFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _5(ff: BooleanSeriesFormat) -> (pd.Series):
    with ff.open() as fh:
        df = _read_dataframe(fh)
        return df.iloc[:, 0]


@plugin.register_transformer
def _6(ff: BooleanSeriesFormat) -> (qiime2.Metadata):
    with ff.open() as fh:
        return qiime2.Metadata(_read_dataframe(fh))


plugin.register_formats(BooleanSeriesFormat, BooleanSeriesDirectoryFormat)

plugin.register_semantic_types(BooleanSeries)

plugin.register_semantic_type_to_format(
    SampleData[BooleanSeries],
    artifact_format=BooleanSeriesDirectoryFormat)


description = ('Predicts a {0} sample metadata column using a {1}. Splits '
               'input data into training and test sets. The training set is '
               'used to train and test the estimator using a stratified '
               'k-fold cross-validation scheme. This includes optional steps '
               'for automated feature extraction and hyperparameter '
               'optimization. The test set validates classification accuracy '
               'of the optimized estimator. Outputs classification results '
               'for test set. For more details on the learning  algorithm, '
               'see http://scikit-learn.org/stable/supervised_learning.html')

inputs = {'table': FeatureTable[Frequency]}

input_descriptions = {'table': ('Feature table containing all features that '
                                'should be used for target prediction.')}

parameters = {
    'base': {
        'random_state': Int,
        'n_jobs': Int,
        'n_estimators': Int % Range(1, None)},
    'standard': {
        'test_size': Float % Range(0.0, 1.0, inclusive_end=False,
                                   inclusive_start=False),
        'step': Float % Range(0.0, 1.0, inclusive_end=False,
                              inclusive_start=False),
        'cv': Int % Range(1, None),
        'parameter_tuning': Bool,
        'optimize_feature_selection': Bool},
    'modified_metadata': {
        'metadata': Metadata,
        'column': Str},
    'regressor': {'stratify': Bool}
}

parameter_descriptions = {
    'base': {'random_state': 'Seed used by random number generator.',
             'n_jobs': 'Number of jobs to run in parallel.',
             'n_estimators': (
                'Number of trees to grow for estimation. More trees will '
                'improve predictive accuracy up to a threshold level, '
                'but will also increase time and memory requirements. This '
                'parameter only affects ensemble estimators, such as Random '
                'Forest, AdaBoost, ExtraTrees, and GradientBoosting.')},
    'standard': {
        'test_size': ('Fraction of input samples to exclude from training set '
                      'and use for classifier testing.'),
        'step': ('If optimize_feature_selection is True, step is the '
                 'percentage of features to remove at each iteration.'),
        'cv': 'Number of k-fold cross-validations to perform.',
        'parameter_tuning': ('Automatically tune hyperparameters using random '
                             'grid search.'),
        'optimize_feature_selection': ('Automatically optimize input feature '
                                       'selection using recursive feature '
                                       'elimination.')},
    'regressor': {
        'stratify': ('Evenly stratify training and test data among metadata '
                     'categories. If True, all values in column must match '
                     'at least two samples.')},
    'estimator': {
        'estimator': 'Estimator method to use for sample prediction.'}
}


plugin.visualizers.register_function(
    function=classify_samples,
    inputs=inputs,
    parameters={
        **parameters['base'],
        **parameters['standard'],
        'metadata': MetadataColumn[Categorical],
        'estimator': Str % Choices(
            ['RandomForestClassifier', 'ExtraTreesClassifier',
             'GradientBoostingClassifier', 'AdaBoostClassifier',
             'KNeighborsClassifier', 'LinearSVC', 'SVC']),
        'palette': Str % Choices(_custom_palettes().keys())},
    input_descriptions=input_descriptions,
    parameter_descriptions={
        **parameter_descriptions['base'],
        **parameter_descriptions['standard'],
        'metadata': ('Categorical metadata column to use as prediction '
                     'target.'),
        **parameter_descriptions['estimator'],
        'palette': 'The color palette to use for plotting.'},
    name='Supervised learning classifier.',
    description=description.format(
        'categorical', 'supervised learning classifier')
)

plugin.visualizers.register_function(
    function=regress_samples,
    inputs=inputs,
    parameters={
        **parameters['base'],
        **parameters['standard'],
        'metadata': MetadataColumn[Numeric],
        **parameters['regressor'],
        'estimator': Str % Choices(
            ['RandomForestRegressor', 'ExtraTreesRegressor',
             'GradientBoostingRegressor', 'AdaBoostRegressor', 'ElasticNet',
             'Ridge', 'Lasso', 'KNeighborsRegressor', 'LinearSVR', 'SVR'])},
    input_descriptions=input_descriptions,
    parameter_descriptions={
        **parameter_descriptions['base'],
        **parameter_descriptions['standard'],
        **parameter_descriptions['regressor'],
        'metadata': 'Numeric metadata column to use as prediction target.',
        **parameter_descriptions['estimator']},
    name='Supervised learning regressor.',
    description=description.format(
        'continuous', 'supervised learning regressor')
)


plugin.visualizers.register_function(
    function=maturity_index,
    inputs=inputs,
    parameters={'group_by': Str,
                'control': Str,
                'estimator': Str % Choices([
                    'RandomForestRegressor', 'ExtraTreesRegressor',
                    'GradientBoostingRegressor', 'SVR', 'Ridge', 'Lasso',
                    'ElasticNet']),
                **parameters['base'],
                **parameters['standard'],
                'metadata': Metadata,
                'column': Str,
                **parameters['regressor'],
                'maz_stats': Bool,
                },
    input_descriptions=input_descriptions,
    parameter_descriptions={
        **parameter_descriptions['base'],
        **parameter_descriptions['standard'],
        'column': 'Numeric metadata column to use as prediction target.',
        'group_by': ('Categorical metadata column to use for plotting and '
                     'significance testing between main treatment groups.'),
        'control': (
            'Value of group_by to use as control group. The regression model '
            'will be trained using only control group data, and the maturity '
            'scores of other groups consequently will be assessed relative to '
            'this group.'),
        'estimator': 'Regression model to use for prediction.',
        **parameter_descriptions['regressor'],
        'maz_stats': 'Calculate anova and pairwise tests on MAZ scores.',
    },
    name='Microbial maturity index prediction.',
    description=('Calculates a "microbial maturity" index from a regression '
                 'model trained on feature data to predict a given continuous '
                 'metadata column, e.g., to predict age as a function of '
                 'microbiota composition. The model is trained on a subset of '
                 'control group samples, then predicts the column value for '
                 'all samples. This visualization computes maturity index '
                 'z-scores to compare relative "maturity" between each group, '
                 'as described in doi:10.1038/nature13421. This method can '
                 'be used to predict between-group differences in relative '
                 'trajectory across any type of continuous metadata gradient, '
                 'e.g., intestinal microbiome development by age, microbial '
                 'succession during wine fermentation, or microbial community '
                 'differences along environmental gradients, as a function of '
                 'two or more different "treatment" groups.'),
    citations=[citations['subramanian2014persistent']]
)
