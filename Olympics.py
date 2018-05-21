import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import os
#from glob import glob
#filenames = glob('./LearnPython/input/Summ*.csv')
# dataframes = [(pd.read_csv(f),f) for f in filenames]
# print(len(dataframes))
# for x,y in dataframes:
#     print(y)
#     print(type(x))
#     print(x.shape)
#print(os.listdir('./input/'))

editions = pd.read_csv('./input/Summer Olympic medalists 1896 to 2008 - EDITIONS.tsv', delimiter='\t',index_col='Edition')
medalists = pd.read_csv('./input/Summer Olympic medalists 1896 to 2008 - ALL MEDALISTS.tsv', delimiter='\t',skiprows=4)
countrycodes = pd.read_csv('./input/Summer Olympic medalists 1896 to 2008 - IOC COUNTRY CODES.csv', delimiter=',')
#print(editions.head())
#print(medalists.head())
#print(medalists.loc[medalists['NOC']== 'YUG'])
#quit()
#print(medalists.shape)
#print(countrycodes.head())
medalibyyearcountry = medalists.pivot_table(index=['Edition'],columns='NOC', values=['Sport'],aggfunc='count').fillna('0')
#print(medalibyyearcountry.head())
print(medalibyyearcountry[('Sport','ZZX')])
#quit()
#medalibyyearcountry.reset_index()
medalibyyearcountry.columns = medalibyyearcountry.columns.droplevel()
#print(medalibyyearcountry.head())
#medalibyyearcountry1 = medalibyyearcountry.iloc[0:,1:].astype(float).pct_change()
medalibyyearcountry = medalibyyearcountry.astype(float).pct_change()
#del medalibyyearcountry1['Edition']
#medalibyyearcountry1['Edit'] = medalibyyearcountry['Edition']
#medalibyyearcountry = medalibyyearcountry1
#print(medalibyyearcountry.head())
#print(medalibyyearcountry.columns)
#print(medalibyyearcountry.shape)
COLUMN_NAMES = ['NOC','Change','Edition']
medalibyyearco = pd.DataFrame(columns=COLUMN_NAMES)
for i in range(len(medalibyyearcountry)):
	a = medalibyyearcountry.iloc[i].to_frame().reset_index()
	a['Edition'] = a.columns.values.tolist()[1] #int(a.iloc[-1][2])
	a.columns = COLUMN_NAMES
	medalibyyearco = medalibyyearco.append(a,ignore_index=True)
	#print(medalibyyearco)
	#break
	
	#print(a)
	#print(a.columns)
	#print(medalibyyearcountry.iloc[i].to_frame().transpose())
	#pass #print(medalibyyearcountry.iloc[i].name)
	#medalibyyearco['Edition'] = medalibyyearcountry['Edition']   #[np.nan for _ in range(len(medalibyyearcountry.columns) - 1)] 
#medalibyyearco = medalibyyearco[['Edition','NOC','Change']]
#print(type(medalibyyearco))
medalibyyearco.sort_values(by=['NOC','Edition'],inplace=True)
medalibyyearco.reset_index(inplace=True,drop=True)
medalibyyearco = medalibyyearco[["Edition","NOC","Change"]] 
#print(medalibyyearco.columns)
#print(medalibyyearco.head())
print(medalibyyearco.loc[medalibyyearco['NOC'] == 'ZZX'])
#print(medalibyyearcountry.iloc[0])
#print(medalibyyearcountry.iloc[:][0])

#print(medalibyyearcountry[('Sport','AFG')])
#a = medalibyyearcountry[('Sport','USA')].to_frame()#.reset_index(0)
#a.columns = ['Edition', 'Medals']
#a.reset_index(level='Edition',col_level=0)
#a.set_index('Edition')
#a['Percent'] = a.astype(float).pct_change() * 100
#print(a)
#print(type(a))
#print(a.columns)
#print(medalibyyearcountry.columns)
#mean_fractions = medalibyyearcountry.expanding().mean().reset_index()
#print(mean_fractions)
#print(mean_fractions.columns)
#print(mean_fractions.loc[:][('Sport','USA')])
# #print(mean_fractions.loc[:,'']
#a = mean_fractions.loc[:][('Sport','USA')].reset_index()
#fractions_change = a.pct_change() * 100
#print(fractions_change.columns)
#b = fractions_change.loc[:][('Sport','USA')].reset_index()
#print(a)
#print(b)
#print(pd.merge(a,b,how='inner',on=['index']))