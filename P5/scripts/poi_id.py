#!/usr/bin/python

import sys
import pickle

from pprint import pprint
from numpy import array
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from time import time

from pprint import pprint

sys.path.append('../tools/')

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

# Select features to use.
orig_features_list = ['poi', 'salary', 'deferral_payments', 'total_payments',
                      'loan_advances', 'bonus', 'restricted_stock_deferred',
                      'deferred_income', 'total_stock_value', 'expenses',
                      'exercised_stock_options', 'other', 'long_term_incentive',
                      'restricted_stock', 'director_fees',
                      'shared_receipt_with_poi', 'to_messages',
                      'from_poi_to_this_person', 'from_messages',
                      'from_this_person_to_poi']


with open('final_project_dataset.pkl', 'r') as data_file:
    data_dict = pickle.load(data_file)


to_exclude = ['TOTAL', 'THE TRAVEL AGENCY IN THE PARK', 'LOCKHART EUGENE E']
my_dataset = {k: {} for k in data_dict.keys() if k not in to_exclude}

# Creates fraction_from/to_poi features
for k in my_dataset.keys():
    if data_dict[k]['from_messages'] == 0:
        my_dataset[k]['fraction_from_poi'] = 0
    elif data_dict[k]['from_messages'] == 'NaN':
        my_dataset[k]['fraction_from_poi'] = 'NaN'
    else:
        my_dataset[k]['fraction_from_poi'] = float(
            data_dict[k]['from_poi_to_this_person']) / float(
            data_dict[k]['to_messages'])

    if data_dict[k]['to_messages'] == 0:
        my_dataset[k]['fraction_to_poi'] = 0
    elif data_dict[k]['to_messages'] == 'NaN':
        my_dataset[k]['fraction_to_poi'] = 'NaN'
    else:
        my_dataset[k]['fraction_to_poi'] = float(
            data_dict[k]['from_this_person_to_poi']) / float(
            data_dict[k]['from_messages'])


features_list = ['poi', 'salary', 'deferral_payments', 'total_payments',
                 'loan_advances', 'bonus', 'restricted_stock_deferred',
                 'deferred_income', 'total_stock_value', 'expenses',
                 'exercised_stock_options', 'other', 'long_term_incentive',
                 'restricted_stock', 'director_fees']

# Constructs data set used for analysis
for k in my_dataset.keys():
    for feature in features_list:
        my_dataset[k][feature] = data_dict[k][feature]

my_features = features_list + ['fraction_from_poi', 'fraction_to_poi']

# Extract features and labels from data set for local testing
data = featureFormat(my_dataset, my_features, sort_keys=True)
labels, features = targetFeatureSplit(data)
labels = array(labels)
features = array(features)
min_max_scaler = MinMaxScaler()
features_scaled = min_max_scaler.fit_transform(features)


pipeline = Pipeline([
    ('pca', PCA()),
    ('nb', GaussianNB())
])
parameters = {
    'pca__n_components': range(7, features.shape[1]+1)
}

grid_search = GridSearchCV(pipeline, parameters, cv=20)

print 'pipeline:', [name for name, _ in pipeline.steps]
print 'parameters:'
pprint(parameters)
t0 = time()
grid_search.fit(features, labels)
print 'done in %0.3fs' % (time() - t0)

print 'Best parameters set:'
best_param = grid_search.best_estimator_.get_params()
for param_name in sorted(parameters.keys()):
    print '\t%s: %r' % (param_name, best_param[param_name])

dump_classifier_and_data(
    Pipeline([
        ('pca', PCA(n_components=best_param['pca__n_components'])),
        ('nb', GaussianNB())
    ]),
    my_dataset,
    my_features
)
