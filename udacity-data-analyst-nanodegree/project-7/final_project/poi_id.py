#!/usr/bin/python
import numpy as np
import pandas as pd
from operator import itemgetter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection  import train_test_split, GridSearchCV
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.naive_bayes import GaussianNB
import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

def format_float(x):
    return int(x*1000.0)/1000.0

def pandas_df_to_markdown_table(df):
    from IPython.display import Markdown, display
    fmt = ['---' for i in range(len(df.columns))]
    df_fmt = pd.DataFrame([fmt], columns=df.columns)
    cols = df.columns.values.tolist()[1:]
    df[cols] = df[cols].applymap(format_float)
    df_formatted = pd.concat([df_fmt, df])
    print(df_formatted.to_csv(sep="|", index=False, decimal='', float_format='%.3f'))

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ["poi"] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
for k,v in data_dict['METTS MARK'].iteritems():
    if k not in ["poi","email_address"]:
        features_list.append(k)

### Task 2: Remove outliers
del data_dict['TOTAL']
del data_dict["LOCKHART EUGENE E"]

df = pd.DataFrame(data_dict).transpose()[features_list]
df = df.replace('NaN', np.nan, regex=True)
def is_NaN(x):
    return x == 'NaN'
df.head(3)
df[features_list[1:]].describe()



### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.

# Before starting to calculate new features, I want to fill NaN values with a predictor. 
# Below functions will create a GaussianNB classifier to predict missing values with respect to other data points. 

# remove NaNs from train data:
def clean_train_data(features):
    for line in features:
        for i,v in enumerate(line):
            if np.isnan(v):
                line[i] = -1.0
    return features
def predict_na_values(df, column):
    print("Predicting missing values for {}.".format(column)) 
    columns = df.columns.values.tolist()
    columns.remove(column)
    # do not translate poi info into missing variables
    columns.remove("poi")
    ok = df[df[column].notnull()]
    ok_features = clean_train_data(ok[columns].values.tolist())
    ok_labels = ok[column].values.tolist()
    nok = df[df[column].isnull()]
    if len(nok)<1:
        print("No missing values for {}!".format(column))
        return
    clf_g = GaussianNB()
    clf_g.fit(ok_features,ok_labels)
    nok_features = clean_train_data(nok[columns].values.tolist())
    pred = clf_g.predict(nok_features)
    df.loc[nok.index,column] = pred

### Fill missing fields with predictions
for column in df.columns.values.tolist():
    ## Do not predict poi 
    if column != "poi":
        predict_na_values(df, column)


        
# List of new created features
df['from_poi_ratio'] = df['from_poi_to_this_person']/df['to_messages']
df['to_poi_ratio'] = df['from_this_person_to_poi']/df['from_messages']


# Parameter selections:

# Parameters selected by weigths acquired from TreeClassifier
selected_list = [
    'poi',
    'to_poi_ratio',
    'from_poi_to_this_person',
    'shared_receipt_with_poi',
    'restricted_stock_deferred',
    'expenses',
    'deferral_payments',
    'from_poi_ratio',
    'salary',
    'to_messages',
    'total_payments',
    'exercised_stock_options',
    'bonus'
]

# Below code will select parameters based on their correlations with poi:

corr_limit = 0.35
corr = df.corr()

def map_(x):
    if abs(x)==1:
        return 0
    elif abs(x)>corr_limit:
        return int(100.0*x)
    return 0
plt.figure(figsize=(12, 10))
sns.heatmap(abs(corr.applymap(map_)), 
            xticklabels=corr.columns.values,
            yticklabels=corr.columns.values)

def extract_parameters_by_correlation(corr, min_corr, depth, selections):
    features = corr.columns.values.tolist()
    new_selections = []
    for sel in selections:
        for f in features:
            if (sel != f) and (f not in selections+new_selections) and (f in corr) and (abs(corr[sel][f]) > min_corr):
                new_selections.append(f)
    selections = selections+new_selections
    if depth < 1:
        return selections
    else:
        return extract_parameters_by_correlation(corr, min_corr, depth-1, selections)

# primary_components are parameters which have correlation with poi or corelation with those that have correlation with poi: 
primary_components = extract_parameters_by_correlation(corr, corr_limit, 2, ["poi"])
primary_components

# Feature disposer to find optimal number of features (sorted by weights): 
def test_different_combinations(feature_list,results):
    feature_list = feature_list[:-1]
    data = featureFormat(my_dataset, ["poi"]+feature_list, sort_keys = True)
    labels, features = targetFeatureSplit(data)
    features_train, features_test, labels_train, labels_test = \
        train_test_split(features, labels, test_size=0.3, random_state=42)
    clf = DecisionTreeClassifier(criterion='gini', min_samples_leaf=1, min_samples_split=2)
    clf.fit(features_train,labels_train)
    y_pred = clf.predict(features_test)
    accuracy, precision, recall, f1, f2 = get_scores(y_pred,labels_test)
    results.append([len(feature_list),accuracy, precision, recall, f1, f2])
    if len(feature_list)>3:
        test_different_combinations(feature_list,results)
    return results

my_dataset = df.to_dict(orient='index')
#final_feature_list = primary_components
#final_feature_list = primary_components+['from_poi_ratio','to_poi_ratio']
#final_feature_list = features_list + ['from_poi_ratio', 'to_poi_ratio']
#final_feature_list = features_list
## parameters weigths extracted from full set

# I tried above lists, but Parameters selected by weigths acquired from TreeClassifier provided best results
final_feature_list = selected_list
### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, final_feature_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
clf_g = GaussianNB()
from sklearn.linear_model import LinearRegression
clf_ln = LinearRegression()
opts_l = {
    "alpha":[0.6,0.85,0.95,1.0],
    "fit_intercept":[True,False]
}
clf_l = GridSearchCV(Lasso(), opts_l)
from sklearn import svm
opts_s = {
    "C":[0.1,1.0,10.0],
    #"kernel":["linear", "poly", "rbf"]
}
clf_s = GridSearchCV(svm.SVC(),opts_s)
opts_t = {
    "criterion":["gini","entropy"],
    "min_samples_leaf":[1,2,5],
    "min_samples_split":[2,4,10]
}
clf_t = GridSearchCV(DecisionTreeClassifier(random_state=0), opts_t)
opts_f = {
    "criterion":["gini","entropy"],
    "n_estimators":[5,10,30,100,200],
    "min_samples_leaf":[1,2,5],
    "min_samples_split":[2,4,10]
}
clf_f = GridSearchCV(RandomForestClassifier(random_state = 0), opts_f)

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
from sklearn.model_selection  import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=0)

models = [
    {"name":"GaussianNB","predictor":clf_g},
    {"name":"Linear Regression","predictor":clf_ln},
    {"name":"Lasso","predictor":clf_l},
    {"name":"SVC","predictor":clf_s},
    {"name":"DecisionTreeClassifier","predictor":clf_t},
    {"name":"RandomForestClassifier","predictor":clf_f}
]

def round_pred(x):
    if x>=0.5:
        return 1.0
    return 0.0

def get_scores(predictions,truth):
    true_negatives = 0
    false_negatives = 0
    false_positives = 0
    true_positives = 0
    for prediction, truth in zip(predictions, labels_test):
        p_int = round_pred(prediction)
        if p_int == 0 and truth == 0:
            true_negatives += 1
        elif p_int == 0 and truth == 1:
            false_negatives += 1
        elif p_int == 1 and truth == 0:
            false_positives += 1
        elif p_int == 1 and truth == 1:
            true_positives += 1
        else:
            print "Warning: Found a predicted label not == 0 or 1. value:{}".format(str(prediction))
    total_predictions = true_negatives + false_negatives + false_positives + true_positives
    accuracy = 1.0*(true_positives + true_negatives)/total_predictions
    precision = 1.0*true_positives/(true_positives+false_positives+0.000001)
    recall = 1.0*true_positives/(true_positives+false_negatives+0.000001)
    f1 = 2.0 * true_positives/(2*true_positives + false_positives+false_negatives+0.000001)
    f2 = (1+2.0*2.0) * precision*recall/(4*precision + recall+0.000001)
    return [accuracy, precision, recall, f1, f2]

def model_predictor(classifier):
    classifier.fit(features_train, labels_train)
    y_pred = classifier.predict(features_test)
    accuracy, precision, recall, f1, f2 = get_scores(y_pred,labels_test)
    return [accuracy, precision, recall, f1, f2]

def run_predictors():
    params = {}
    scores = []
    for predictor in models:
        accuracy, precision, recall, f1, f2 = model_predictor(predictor["predictor"])
        scores.append([predictor["name"], accuracy, precision, recall, f1, f2])
        # print("{} accuracy: {:.2f}, precision: {:.2f}, recall: {:.2f}, F1: {:.2f}, F2: {:.2f}".format(predictor["name"], accuracy, precision, recall, f1, f2))
        if hasattr(predictor["predictor"],"best_estimator_"):
            params[predictor["name"]] = predictor["predictor"].best_estimator_
        else:
            params[predictor["name"]] = predictor["predictor"]
        score_table = pd.DataFrame(scores, columns=["Classifier", "Accuracy", "Precision", "Recall", "F1 Score", "F2 Score"])
    return params, score_table

params, score_table = run_predictors()
score_table

clf = params["DecisionTreeClassifier"]
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, final_feature_list)