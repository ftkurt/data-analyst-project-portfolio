
# Question 1
> Summarize for us the goal of this project and how machine learning is useful in trying to accomplish it. As part of your answer, give some background on the dataset and how it can be used to answer the project question. Were there any outliers in the data when you got it, and how did you handle those?  [relevant rubric items: “data exploration”, “outlier investigation”]

This project aims to build an efficient machine learning algorithm to programatically detect potential persons of interest within data. The model is expected to make the best use of available features withing Enron Dataset as well as creating new features to predict the poi from the available features. 

Enron data has 146 data points, 18 of which belong POIs. Each datapoint has 14 features. Features cover a wide variety of data from financial attributes like salary, bonuses, payments to email statistics like emails to POI, and emails from POI. Almost all features have missing values. We should also address this issue during this project.

Dataset has one outlier data which belongs to an entry named "TOTAL". This entry clearly points to the subtotal for the entire dataset, and thereby should be discarded. Discaridng this entry leaves 18 POI and 127 non-POI entries. With 12.4% POI within dataset, data is skewed towards non-POIs. We should keep an eye on this insight during score extractions from models. Assuming we are primarily concerned with detecting as many POIs as possible, recall will be the primary score we will be looking to.

# Question 2
> What features did you end up using in your POI identifier, and what selection process did you use to pick them? Did you have to do any scaling? Why or why not? As part of the assignment, you should attempt to engineer your own feature that does not come ready-made in the dataset -- explain what feature you tried to make, and the rationale behind it. (You do not necessarily have to use it in the final analysis, only engineer and test it.) In your feature selection step, if you used an algorithm like a decision tree, please also give the feature importances of the features that you use, and if you used an automated feature selection function like SelectKBest, please report the feature scores and reasons for your choice of parameter values.  [relevant rubric items: “create new features”, “intelligently select features”, “properly scale features”]

Since the number of variables was within acecptable range, I started with the full set to decide on an model parameters. Later on I was planning on reducing number of parameters. First approach was using Tree Classifier parameter weights extracted from trained classifier usign full variable set. 

#### Here is list of parameters with non-zero values:

|Parameter|Weight|
|---|---|
|from_poi_ratio|0.410935|
|total_stock_value|0.188715|
|bonus|0.124453|
|shared_receipt_with_poi|0.106765|
|to_messages|0.105462|
|restricted_stock|0.063670|

My second approach was finding variables having > 0.9 correlation with poi and >0.9 correlation with those that have >0.9 correlation with poi, and so forth until a depth value. I used a depth of 1. 

I did not use any scaling, knowing scaling would have no effect on tree classifiers which I believed will be optimal predictors for this project. However, I filled missing values each with a **GaussianNB** predictor that used all parameters other than the original one plus the **poi** parameter. Later on the predictions from **GaussianNB** predictor are used to fill missing values.

I created two new variables, one for **ratio of mails received from POIs**, and the other for **ratio of mail sent to POIs**. I believe the numbers of mails sent to POI or received thereof would not give meaningful info. SOme might be sending too many emails or too few emails overall. In this case, having the ratio for their POI related emails would provide better insight.

# Question 3
> What algorithm did you end up using? What other one(s) did you try? How did model performance differ between algorithms?  [relevant rubric item: “pick an algorithm”]

I decided to try all classifiers including linear models with an added rounding layer. From Linear models GaussianNB, and Linear Regression, the predictors are used without parameter tuning, since they dont have parameter tuning. For Lasso and other regular classifiers, I used a set of parameters with Grid Search. All scores listed below belong to best parameter combinations.

#### Full Feature Set Results:

Classifier|Accuracy|Precision|Recall|F1 Score|F2 Score
---|---|---|---|---|---
GaussianNB|0.886|0.33|0.25|0.286|0.263
Linear Regression|0.864|0.25|0.25|0.25|0.25
Lasso|0.8636363636363636|0.25|0.25|0.25|0.25
SVC|0.9090909090909091|0.0|0.0|0.0|0.0
DecisionTreeClassifier|0.841|0.2|0.25|0.22|0.238
RandomForestClassifier|0.932|1.0|0.25|0.4|0.294

#### DecisionTreeClassifier Weights Feature Selector

Classifier|Accuracy|Precision|Recall|F1 Score|F2 Score
---|---|---|---|---|---
GaussianNB|0.886|0.4|0.5|0.444|0.476
Linear Regression|0.91|0.5|0.25|0.333|0.278
Lasso|0.91|0.5|0.25|0.333|0.278
SVC|0.91|0.0|0.0|0.0|0.0
DecisionTreeClassifier|0.886|0.4|0.5|0.444|0.476
RandomForestClassifier|0.864|0.0|0.0|0.0|0.0

#### Correlation (depth = 1) Results:

Classifier|Accuracy|Precision|Recall|F1 Score|F2 Score
---|---|---|---|---|---
GaussianNB|0.864|0.25|0.25|0.25|0.25
Linear Regression|0.886|0.333|0.25|0.2865|0.263
Lasso|0.91|0.5|0.25|0.333|0.278
SVC|0.91|0.0|0.0|0.0|0.0
DecisionTreeClassifier|0.91|0.5|1.0|0.67|0.833
RandomForestClassifier|0.977|1.0|0.75|0.857|0.789



**Correlation @ Depth = 1** gave best results with highest Recall score of DecisionTreeClassifier (100%) and highest Precision of RandomForestClassifier (100%). 

Since finding all POIs is more important than precisely finding correct POIs, the primary score is Recall. Therefore, I decided to go with **DecisionTreeClassifier**.

# Question 4
> What does it mean to tune the parameters of an algorithm, and what can happen if you don’t do this well?  How did you tune the parameters of your particular algorithm? What parameters did you tune? (Some algorithms do not have parameters that you need to tune -- if this is the case for the one you picked, identify and briefly explain how you would have done it for the model that was not your final choice or a different model that does utilize parameter tuning, e.g. a decision tree classifier).  [relevant rubric items: “discuss parameter tuning”, “tune the algorithm”]

Classifiers have a lot of parameters in order to decide their behaviors with fitting data and classifiying input. Each data will need different set of parameter values to classify input the most efficiently. Parameter tuning is trying to find this best parameters or getting close enough.

For this project I went through list of parameters available for tuning for each classifier. Each classifier is then wrapped with GridSearch alongside with this parameter ranges. Gridsearch, then tries all combinations of these parameter valu lists, and returns the best predictor configuration.

Parameters tuned for each model are as below:

#### Lasso

    parameters = {
        "alpha":[0.6,0.85,0.95,1.0],
        "fit_intercept":[True,False]
    }

#### SVM
    parameters = {
        "C":[0.1,1.0,10.0]
    }

#### DecisionTreeClassifier
    parameters = {
        "criterion":["gini","entropy"],
        "min_samples_leaf":[1,2,5],
        "min_samples_split":[2,4,10]
    }

#### RandomForestClassifier
    parameters = {
        "criterion":["gini","entropy"],
        "n_estimators":[5,10,30,100,200],
        "min_samples_leaf":[1,2,5],
        "min_samples_split":[2,4,10]
    }


At the end of parameter tuning I decided to go with **DecisionTreeClassifier**. The best parameters found with this classifier are as below:

    DecisionTreeClassifier(criterion='gini', min_samples_leaf=5, min_samples_split=2)

# Question 5
> What is validation, and what’s a classic mistake you can make if you do it wrong? How did you validate your analysis?  [relevant rubric items: “discuss validation”, “validation strategy”]

Validation is testing the classifier / model built for the purpose or classifying new data. To do this, original data should be split into two groups: **train** and **test**

Train data is used to build model/classifier. Test data is used to validate if the model behaves as expected. Test data is expected to be completely new to the classifier at the time testing. Test data can also be split into validation and test for bling testing. But in this project we only split data into train and test.

In model building stage of this project we also split data into train and test. We first fitted out classifiers with train dataset. Later on we evaluated our classifiers based on test data. 

However this type of evaluation is not deterministic enough. To get results better evaluating classifier n-fold validation is used. In this method, data is reshuffled n times and tested with split results for each fold. Overall results are then combined. 

# Question 6
> Give at least 2 evaluation metrics and your average performance for each of them.  Explain an interpretation of your metrics that says something human-understandable about your algorithm’s performance. [relevant rubric item: “usage of evaluation metrics”]

**Accuracy:** The ratio of which prediction of POIs match the truth about employee

**Recall:** The ratio of POIs being identified.

**Precision:** The ratio of identified entries being POIs

My DecisionTreeClassifier achieved following scores for these metrics:

#### Using Train & Test Split: 

* Accuracy: **0.91**

* Recall: **1.0**

* Precision: **0.5**


#### Using Final Testing Script (Cross-Validation: cv = 1000):

* Accuracy: **0.85860**

* Recall: **0.39800**

* Precision: **0.46468**

The difference between my results and CV results is mostly due to train-test split being in favor my results, which shows how cross validation can help better evaluate a classifier. 
