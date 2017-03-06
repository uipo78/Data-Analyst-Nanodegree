
# The Enron Scandal: A Machine Learning Exercise


```python
import pickle

from collections import defaultdict
from pprint import pprint
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

PATH = 'Q:\\Program Files\\Programming Applications\\Projects\\Github\\clones\\ud120-projects\\final_project\\'

features_list = ['poi', 'salary', 'deferral_payments', 'total_payments',
                 'loan_advances', 'bonus', 'restricted_stock_deferred',
                 'deferred_income', 'total_stock_value', 'expenses',
                 'exercised_stock_options', 'other', 'long_term_incentive',
                 'restricted_stock', 'director_fees',
                 'shared_receipt_with_poi', 'to_messages',
                 'from_poi_to_this_person', 'from_messages',
                 'from_this_person_to_poi']


with open(PATH + 'final_project_dataset.pkl', 'r') as data_file:
    data_dict = pickle.load(data_file)
```

## Short Questions
### Question 1 
__*Summarize for us the goal of this project and how machine learning is useful in trying to accomplish it. As part of your answer, give some background on the dataset and how it can be used to answer the project question. Were there any outliers in the data when you got it, and how did you handle those?*__

The goal of this project was to build a model that predicts whether an individual was a person of interest (POI) in the Enron scandal. The model was a binomial classifier, fitted on a dataset of 146 records of individuals with fourteen financial and six email features. Of the 146 individuals, 18 were POI.

It should be mentioned that the dataset wasn't replete with information. Take a look at the number of missing values for each feature: 


```python
counter = defaultdict(int)
for name in data_dict.keys():
    for feature in data_dict[name].keys():
        if data_dict[name][feature] == 'NaN':
            counter[feature] += 1

pprint(sorted(counter.items(), key=lambda x: x[1], reverse=True))
```

    [('loan_advances', 142),
     ('director_fees', 129),
     ('restricted_stock_deferred', 128),
     ('deferral_payments', 107),
     ('deferred_income', 97),
     ('long_term_incentive', 80),
     ('bonus', 64),
     ('to_messages', 60),
     ('shared_receipt_with_poi', 60),
     ('from_poi_to_this_person', 60),
     ('from_messages', 60),
     ('from_this_person_to_poi', 60),
     ('other', 53),
     ('salary', 51),
     ('expenses', 51),
     ('exercised_stock_options', 44),
     ('restricted_stock', 36),
     ('email_address', 35),
     ('total_payments', 21),
     ('total_stock_value', 20)]
    

It should also be mentioned that three records were not used to fit the model. These records and the cause for their exclusion were:
* TOTAL, THE TRAVEL AGENCY IN THE PARK, since neither are individuals
* LOCKHART EUGENE E, since every one of his features were NaN (see below)


```python
for name in data_dict.keys():
    for feature in [f for f in data_dict[name].keys() if f != 'poi']:
        if data_dict[name][feature] != 'NaN':
            break
    else:
        print name
```

    LOCKHART EUGENE E
    

See the beginning of the example code in question 2 (in particular, the initialization of 'my_dataset') for detail on the method by which these outlier entries were excluded. 

### Question 2 
__*What features did you end up using in your POI identifier, and what selection process did you use to pick them? Did you have to do any scaling? Why or why not? As part of the assignment, you should attempt to engineer your own feature that does not come ready-made in the dataset -- explain what feature you tried to make, and the rationale behind it.*__

Since I couldn't intuitively justify which features should/shouldn't be included in the analysis, I decided to let an unsupervised machine learning algorithm choose&mdash;namely, principal components analysis (PCA). But before running this algorithm, I needed to do some feature engineering.

Feature engineering consisted of the following processes: scaling those features included in the list 'features_to_scale' (shown below) and creating two new features from four raw features. The scaling method is pretty self-explanatory (see code below). The two new features measure the proprotion of an individual's emails that were sent from/to a POI. I scrap the four raw features in favor of two new features because, intuitively, the frequency of contact between POI seemed to be easier to understand and more relevant than, say, a normalized number of emails sent to/from a POI (and one whose scale would be consistent across all individuals). 

Notice that every feature is normalized. This is necessary for PCA, as without normalized features, PCA may incorrectly identify the principal component encoding the most variance. Example: suppose that the variance in salary is small but still has a value larger than one, and that the variance in the frequency of emails sent to/from a POI are large but (necessarily) has a value  less than or equal to 1. Then, PCA will favor principal components encoding the variance in salary over the variance in email frequency, because of the larger magnitude of the variance in salary; this is the exact opposite of what we would want. 


```python
to_exclude = ['TOTAL', 'THE TRAVEL AGENCY IN THE PARK', 'LOCKHART EUGENE E']
my_dataset = {k: {} for k in data_dict.keys() if k not in to_exclude}

# Creates fraction_from/to_poi features
for k in my_dataset.keys():
    if data_dict[k]['from_messages'] == 0:
        my_dataset[k]['fraction_from_poi'] = 0
    elif data_dict[k]['from_messages'] == 'NaN':
        my_dataset[k]['fraction_from_poi'] = 'NaN'
    else:
        my_dataset[k]['fraction_from_poi'] = \
            float(data_dict[k]['from_poi_to_this_person'])/float(data_dict[k]['to_messages'])

    if data_dict[k]['to_messages'] == 0:
        my_dataset[k]['fraction_to_poi'] = 0
    elif data_dict[k]['to_messages'] == 'NaN':
        my_dataset[k]['fraction_to_poi'] = 'NaN'
    else:
        my_dataset[k]['fraction_to_poi'] = \
            float(data_dict[k]['from_this_person_to_poi'])/float(data_dict[k]['from_messages'])


features_to_scale = ['salary', 'deferral_payments', 'total_payments',
                     'loan_advances', 'bonus', 'restricted_stock_deferred',
                     'deferred_income', 'total_stock_value', 'expenses',
                     'exercised_stock_options', 'other', 'long_term_incentive',
                     'restricted_stock', 'director_fees']

# Constructs data set used for analysis as well as scales selected features
for k in my_dataset.keys():
    for feature in ['poi'] + features_to_scale:
        if feature in feature_to_scale and data_dict[k][feature] != 'NaN':
            my_dataset[k][feature] = \
                float(data_dict[k][feature])/float(data_dict['TOTAL'][feature])
        else:
            my_dataset[k][feature] = data_dict[k][feature]
```

### Question 3
__*What algorithm did you end up using? What other one(s) did you try? How did model performance differ between algorithms?*__

Below is a table of the tested algorithms. Excluding the Gaussian Naive Bayes Classifier, each algorithm was tested with several different parameters.


| Classifier                      | Precision | Recall | PCA Components |
| :-------------------------------|------:|------:|------:|
| Gaussian Naive Bayes Classifier | 0.358 | 0.301 | 10 |
| Support Vector Classifier       | 0.549 | 0.104 | 11 |
| Random Forest Classifier        | 0.376 | 0.148 | 13 |

Let's talk about each of these algorithms. As you can see, SVC performed quite well in precision but not well in recall. I attempted to tune the parameters in such a way as to increase recall. But it may be that the lack of balance in the number of POI and non-POI individuals in the data set is limiting SVC's performance in recall. The Random Forest Classifier performed nearly the same as SVC, but took *much* longer to execute than SVC. Gaussian Naive Bayes appears, for our purposes, to have the most desireable performance. What's more, it executed very quickly (0.264s) and it didn't require any parameter tuning (this does not include PCA, which found 10 components to be the most optimal).

### Question 4
__*What does it mean to tune the parameters of an algorithm, and what can happen if you don’t do this well?  How did you tune the parameters of your particular algorithm?*__ 

Parameter tuning is the act of adjusting factors which influence a model's development in order to achieve a desired outcome (An example of a desired outcome: to more strictly penalize overcomplexity). Poorly tuned parameters can, as you might expect, lead to undesired outcomes. For example, suppose that we wish to perform regression analysis. Suppose further that we are concerned about overfitting. To that end, we perform LASSO. Now, if we poorly choose a value for lambda (the model's penalty term), such that lambda is very close to 0, we would essentially introduce no penalty to overcomplexity and would be acting against our objective to avoid overfitting; our regularized regression model would essetially be an OLS regression model.

In this project, parameter tuning was performed by sklearn's GridSearchCV function. See the example code below for more detail.


```python
pipeline = Pipeline([
    ('pca', PCA()),
    ('rf', RandomForestClassifier())
])
parameters = {
    'pca__n_components': range(10, 17),
    'rf__n_estimators': range(10, 80, 10),
    'rf__min_samples_split': range(2, 8),
    'rf__random_state': [1]
}

grid_search = GridSearchCV(pipeline, parameters, cv=10)
```

### Question 5
__*What is validation, and what’s a classic mistake you can make if you do it wrong? How did you validate your analysis?*__

Validation is the process of assessing a model's capacity to generalize. That is, validation assesses the performance of a model on a new data set independent of the data set used to fit the model. The classic mistake in validation is overfitting&mdash;having very good performance 

10-fold cross validation via the GridSearchCV function was used in poi_id. An interesting note: tester.py used StratifiedShuffleSplit as a method to partition the data set. This choice may be a consequence of the fact that there are many more non-POI to POI; StratifiedShuffleSplit ensures that POI to non-POI composition for both the training and testing data sets are more balanced.

### Question 6
__*Give at least 2 evaluation metrics, and your average performance for each of them. Explain an interpretation of your metrics that says something human-understandable about your algorithm's performance*__

For this assignment, I considered two evaluation metrics: recall and precision. We can interpret recall in the context of this project as follows: the probability of the model predicting a person as POI, given that the person is actually a POI. Precision, in the context of this project, is the probability of a person actually being a POI, given that the model predicted the person as such. In other words, a precision value of 0.3 tells us that if our model identified 100 persons as POI, then it is likely that 30 of the 100 are POI. Therefore, the Gaussian Naive Bayes Classifier would perform as follows: if an individual is actually a POI, then the model would correctly identify him/her with probability 0.301; if the model identified a person as POI, then there is a 0.358 probability that the person is a POI.
