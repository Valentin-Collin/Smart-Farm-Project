import pandas as pd
import matplotlib.pyplot as plt
import pickle as pk
import numpy as np

from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
from sklearn.linear_model import LogisticRegression
import seaborn as sns

PATH = 'C:/Users/valen/Desktop/SmartFarm/Crop_recommendation.csv'
  
# Load the CSV file data into 
# data variable using pandas 
data = pd.read_csv(PATH) 

 
# Return the first five rows of CSV file 
print(data.head())

 
# Return information about the datatype, 
# NULL type of the columns of CSV file
print(data.info())

# describe 
print(data.describe())

print(data['label'].unique())

 
# Return the count of each unique label 
print(data['label'].value_counts())

 
# over all distribution 
  
plt.rcParams['figure.figsize'] = (10, 10) 
plt.rcParams['figure.dpi'] = 60
  
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'] 
  
for i, feat in enumerate(features): 
    plt.subplot(4, 2, i + 1) 
    sns.histplot(data[feat], color='greenyellow') 
    if i < 3: 
        plt.title(f'Ratio of {feat}', fontsize=12) 
    else: 
        plt.title(f'Distribution of {feat}', fontsize=12) 
    plt.tight_layout() 
    plt.grid()

#plt.show()

plt.figure(1)

sns.pairplot(data, hue='label')  
plt.figure(2)

fig, ax = plt.subplots(1, 1, figsize=(15, 9)) 


sns.heatmap(data.corr(numeric_only=True), annot=True, cmap='viridis') 

ax.set(xlabel='features') 
ax.set(ylabel='features') 
  
plt.title('Correlation between different features', fontsize=15, c='black') 

plt.figure(3)
plt.show() 

# Put all the input variables into features vector 
features = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]#X
  
# Put all the output into labels array 
labels = data['label']#Y

X_train, X_test, Y_train, Y_test = train_test_split(features, 
                                       labels, 
                                       test_size=0.2,#Ensemble de test fait pour évaluer les performances du modèle sur les données qu'il n'a pas vues pendant l'entrainement
                                       train_size=0.8,#Ensemble d'entrainement utilisé pour entraîner le modèle 
                                       random_state=42)#Permet d'assurer la séparation des données en ensembles d'entrainements et de tests


# Pass the training set into the 
# LogisticRegression model from Sklearn 
LogisticReg = LogisticRegression(random_state=42,max_iter=10000).fit(X_train, Y_train) 
  
# Predict the values for the test dataset 
predicted_values = LogisticReg.predict(X_test) 
  
# Measure the accuracy of the test set using accuracy_score metric 

accuracy = metrics.accuracy_score(Y_test, predicted_values) 

print("Predicted_values: ", predicted_values)
print("Accuracy: ", accuracy)

# Get detail metrics 
print(metrics.classification_report(Y_test, predicted_values))

    
filename = 'LogisticRegresion.pkl'
MODELS = 'C:/Users/valen/Desktop/SmartFarm/'
# Use pickle to save ML model 
pk.dump(LogisticReg, open(MODELS + filename, 'wb')) 








