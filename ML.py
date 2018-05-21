import pandas as pd
import pickle
import quandl, math, datetime,time
import numpy as np
import scipy
#cross_validation as changed to model_selection
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import style


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
#print(df.head())
#X = Features
#y - labels or output

X = np.array(df.drop(['label'],axis = 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
#print(X_lately)
X = X[:-forecast_out]
#quit()
#X= X[:-forecast_out+1]
#print(df[df.isnull().any(axis=1)])
#df.dropna(inplace=True)
#print(X)
#make sure length of trest and train is same
df.dropna(inplace=True) 

y=np.array(df['label'])
#print(y)

X_train, X_test, y_train, y_test = model_selection.train_test_split(X,y,test_size=0.2)

# clf = LinearRegression(n_jobs=-1)
# #clf =svm.SVR(kernel='poly')
# clf.fit(X_train,y_train)
# with open('./input/linerregression.pickle','wb') as f:
# 	pickle.dump(clf,f)
pickle_in = open('./input/linerregression.pickle','rb')
clf = pickle.load(pickle_in)
accuracy = clf.score(X_test,y_test)
#print(accuracy)

forecast_set = clf.predict(X_lately)
print(forecast_set, accuracy, forecast_out)


df['Forecast'] = np.nan
#print(df.tail())

last_date = df.iloc[-1].name
#print(last_date)
#last_unix = last_date.timestamp()
last_unix = time.mktime(datetime.datetime.strptime(str(last_date), "%Y-%m-%d %H:%M:%S").timetuple())
#print(last_unix1)
#print(last_unix)
one_day = 86400
next_unix = last_unix + one_day
#next_date = datetime.datetime.fromtimestamp(next_unix)
#print(next_date)
for i in forecast_set:
	next_date = datetime.datetime.fromtimestamp(next_unix)
	#print(next_date)
	next_unix += one_day
	df.loc[next_date] = [np.nan for _ in range(len(df.columns) - 1)] + [i]

print(df.tail(40))
df.to_pickle("./input/GOOGL.pkl")