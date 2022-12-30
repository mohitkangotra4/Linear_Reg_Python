#!/usr/bin/env python
# coding: utf-8

# In[105]:


import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats


# ## loading data
# 

# In[106]:


df = pd.read_csv(r'C:\Users\Mohit\Downloads\Campaign-Data.csv') #savinf data as df


# In[107]:


df.columns


# ### Amount collected will be our target variable to define our marketing strategy

# In[4]:


#checking data types
df.info()


# In[5]:


df.isna().sum() # checking for na values in data


# ## convert ['Calenderdate'] from object to datetime dtype

# In[108]:


df['Calendardate']= pd.to_datetime(df['Calendardate'])
df['Month']= df['Calendardate'].dt.month
df['Year']= df['Calendardate'].dt.year


# ## Ad Hoc Analysis

# In[109]:


df['Client Type'].value_counts(normalize=True)


# In[110]:


pd.crosstab(df['Number of Competition'], df['Client Type'], margins=True, normalize=True)


# ### continuing the analysis of the Number of Competition category (Catrgorical Analysis)

# In[111]:


df.groupby('Number of Competition').mean()


# #### Note: Above we can see Although majority of market is in low competition but our reveue and sales (almost double) are from High competition

# In[112]:


df.groupby(df['Client Type']).mean()


# ## Diving into Correlation Analysis

# In[113]:


df.corr()[['Amount Collected']]


# In[114]:


# consolated strategy for Targeting
cm = sns.light_palette("green", as_cmap=True)
correlation_analysis = pd.DataFrame(df[['Amount Collected', 'Campaign (Email)', 'Campaign (Flyer)', 'Campaign (Phone)',
       'Sales Contact 1', 'Sales Contact 2', 'Sales Contact 3',
       'Sales Contact 4', 'Sales Contact 5']].corr()['Amount Collected']).reset_index()


# In[119]:


correlation_analysis.columns = ['Impact Variables', 'Degree of Linear Impact']
# removind amount collecetd from the df
correlation_analysis= correlation_analysis[correlation_analysis['Impact Variables']!='Amount Collected']
# sorting according to the degree of correlation
correlation_analysis=correlation_analysis.sort_values('Degree of Linear Impact', ascending=False)
correlation_analysis.style.background_gradient(cmap=cm).set_precision(2)


# ### doint the above steps but modling the strategy to get correlation according to account type

# In[124]:


import seaborn as sns
cm= sns.light_palette('blue', as_cmap=True)

correlation_analysis = pd.DataFrame(df.groupby('Client Type')[['Amount Collected','Campaign (Email)', 'Campaign (Flyer)', 'Campaign (Phone)',
       'Sales Contact 1', 'Sales Contact 2', 'Sales Contact 3',
       'Sales Contact 4', 'Sales Contact 5']].corr()['Amount Collected']).reset_index()


# In[125]:


# renaming columns
correlation_analysis.columns=['Account Type', 'Variable Impact on Sales', 'Impact']
#remoing amount collected rows 
correlation_analysis=correlation_analysis[correlation_analysis['Variable Impact on Sales']!='Amount Collected']
# sording in Descending order of Linear Impact(Correlation)
correlation_analysis=correlation_analysis.sort_values(['Account Type','Impact'], ascending=False)
correlation_analysis.style.background_gradient(cmap=cm).set_precision(2)


# ## Building a Linear Regression Model

# In[126]:


import statsmodels.api as sm
import statsmodels.formula.api as smf

#Little data cleaning
df.columns=[ mystring.replace(' ','_') for mystring in df.columns]
df.columns=[mystring.replace('(', '') for mystring in df.columns]
df.columns=[mystring.replace(')', '') for mystring in df.columns]
df.columns


# In[127]:


results= smf.ols('Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + Sales_Contact_1 +         Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5', data=df ).fit()
print(results.summary())


# In[128]:


df1 = pd.read_html(results.summary().tables[1].as_html(),header=0,index_col=0)[0]
df1=df1.reset_index()
df1=df1[df1['P>|t|']<0.05][['index','coef']]
df1


# ## Regression Analysis (Broken for different account types)

# In[129]:


consolidated_summary=pd.DataFrame() # creating new empty data frame
for acctype in list(set(list(df['Client_Type']))):
    temp_data=df[df['Client_Type']==acctype].copy()
    results= smf.ols('Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + Sales_Contact_1 +         Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5', data=temp_data).fit()
    df1 = pd.read_html(results.summary().tables[1].as_html(), header=0, index_col=0)[0].reset_index()
    df1=df1[df1['P>|t|']<0.05][['index','coef']]
    df1.columns=['Variable','Coefficent (Impact)']
    df1['Account Type']=acctype
    df1=df1.sort_values('Coefficent (Impact)', ascending=False)
    df1=df1[df1['Variable']!='Intercept']
    print(acctype)
    consolidated_summary=consolidated_summary.append(df1)
    print(df1)
    #print the results.summary()


# In[130]:


consolidated_summary


# In[131]:


consolidated_summary.reset_index(inplace=True)
consolidated_summary.drop('index', inplace=True, axis=1)
consolidated_summary.columns=['Variable','Return_on_Investment','Account_Type']
consolidated_summary['Return_on_Investment']=consolidated_summary['Return_on_Investment'].apply(lambda x : round(x, 1))
consolidated_summary.style.background_gradient(cmap='RdYlGn') 


# In[135]:


consolidated_summary.to_csv(r'C:\Users\Mohit\Downloads\consolidated_summary.csv')

