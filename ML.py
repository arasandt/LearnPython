import pandas as pd
import quandl, math
import numpy as np
import scipy
#cross_validation as changed to model_selection
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression

df = quandl.get('WIKI/GOOGL')
#print(df.head)
df = df[['Adj. Open','Adj. High','Adj. Low','Adj. Close','Adj. Volume',]]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Close']) / df['Adj. Close'] * 100.0
df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) / df['Adj. Open'] * 100.0
df = df[['Adj. Close','HL_PCT','PCT_change','Adj. Volume']]
#print(df.tail())
forecast_col = 'Adj. Close'
df.fillna(-99999,inplace=True)

#forecast_out = int(math.ceil(0.01*len(df)))
#forecast_out = (0.01*len(df))
forecast_out = math.ceil(0.01*len(df))
print(forecast_out)
#print(type(forecast_out))
df['label'] = df[forecast_col].shift(-forecast_out)
df.dropna(inplace=True) 
#print(df.head())
#X = Features
#y - labels or output

X = np.array(df.drop(['label'],axis = 1))
X = preprocessing.scale(X)

#X= X[:-forecast_out+1]
#print(df[df.isnull().any(axis=1)])
#df.dropna(inplace=True)
#print(X)
#make sure length of trest and train is same
y=np.array(df['label'])
#print(y)

X_train, X_test, y_train, y_test = model_selection.train_test_split(X,y,test_size=0.2)

clf = LinearRegression(n_jobs=-1)
#clf =svm.SVR(kernel='poly')
clf.fit(X_train,y_train)
accuracy = clf.score(X_test,y_test)
print(accuracy)


