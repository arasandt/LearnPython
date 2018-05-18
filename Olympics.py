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
#print(medalists.shape)
#print(countrycodes.head())
medalibyyearcountry = medalists.pivot_table(index=['Edition'],columns='NOC', values=['Sport'],aggfunc='count').fillna('0')
#medalibyyearcountry.divide(medalibyyearcountry.sum)
#print(medalibyyearcountry)
mean_fractions = medalibyyearcountry.expanding().mean().reset_index()
#print(mean_fractions)
#print(mean_fractions.columns)
#print(mean_fractions.loc[:][('Sport','USA')])
# #print(mean_fractions.loc[:,'']
a = mean_fractions.loc[:][('Sport','USA')].reset_index()
fractions_change = a.pct_change() * 100
#print(fractions_change.columns)
b = fractions_change.loc[:][('Sport','USA')].reset_index()
#print(a)
#print(b)
print(pd.merge(a,b,how='inner',on=['index']))