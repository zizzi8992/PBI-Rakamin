# -*- coding: utf-8 -*-
"""FinalTask-ML.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1G4LGqHli2c3pfqy33wlyQDtgGHybm8AJ

# PBI KALBE
## Machine Learning Challenge
"""

# Commented out IPython magic to ensure Python compatibility.
# IMPORT LIBRARY
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from statsmodels.tsa.statespace.sarimax import SARIMAX
!pip install pmdarima
import pmdarima as pm
# %matplotlib inline

# LOAD DATA
df_customer = pd.read_csv('Case Study - Customer.csv', delimiter=';')
df_product = pd.read_csv('Case Study - Product.csv', delimiter=';')
df_store = pd.read_csv('Case Study - Store.csv', delimiter=';')
df_transaction = pd.read_csv('Case Study - Transaction.csv', delimiter=';')

# EDA
df_customer.head()

df_customer.dtypes

df_customer.isnull().sum()

# FILL MISSING VALUES
df_customer.fillna(method='ffill', inplace=True)

# CONVERT CATEGORICAL TO NUMERICAL
df_customer['Marital Status'] = df_customer['Marital Status'].apply(lambda x: 1 if x == 'Married' else 0)

# CONVERT INCOME INTO FLOAT DATA TYPE
df_customer['Income'] = df_customer['Income'].apply(lambda x: x.replace(',', '.')).astype(float)

df_customer.head()

df_transaction.head()

df_transaction.dtypes

# CONVERT DATE DATA TYPE TO datetime
df_transaction['Date'] = pd.to_datetime(df_transaction['Date'], format='%d/%m/%Y')

# MERGE df_transaction AND df_customer
merged_df = pd.merge(df_transaction, df_customer, on='CustomerID', how='left')
merged_df.head()

merged_df.info()

# AGGREGATE DATA
agg = {
    'TransactionID': 'count',
    'Qty': 'sum',
    'TotalAmount': 'sum'
}
cluster_df = merged_df.groupby('CustomerID').aggregate(agg).reset_index()
cluster_df.head()

# SCALE INTO SIMILAR RANGE
scaler = StandardScaler()
scaled_df = scaler.fit_transform(cluster_df[['TransactionID', 'Qty', 'TotalAmount']])
scaled_df = pd.DataFrame(scaled_df, columns=['TransactionID', 'Qty', 'TotalAmount'])
scaled_df.head()

"""### CLUSTERING"""

# FINDING OPTIMAL NUMBER
inertia = []
max_clusters = 11
for n_cluster in range(1, max_clusters):
    kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=n_cluster)
    kmeans.fit(cluster_df.drop('CustomerID', axis=1))
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(10,8))
plt.plot(np.arange(1, max_clusters), inertia, marker='o')
plt.xlabel('Number of cluster')
plt.ylabel('Inertia')
plt.xticks(np.arange(1, max_clusters))
plt.show()

"""From the graph above we can decide that the number of cluster that doesn't signifcant is 3"""

# CREATE THE CLUSTER
n_cluster = 3
kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=n_cluster)
kmeans.fit(cluster_df.drop('CustomerID', axis=1))
cluster_df['Cluster'] = kmeans.labels_

# PLOT THE CLUSTER
cluster_df.plot(kind='scatter', x='Qty', y='TotalAmount', c='Cluster', cmap='viridis', figsize=(10,8), legend=True)
plt.show()

#--
# MERGE DATA
merged_df = pd.merge(df_transaction, df_product, on='ProductID', how='left')
merged_df = pd.merge(merged_df, df_store, on='StoreID', how='left')
merged_df = pd.merge(merged_df, df_customer, on='CustomerID', how='left')
merged_df

merged_df.info()

"""REGRESSION"""

# DF FOR REGRESSION
reg_df = df_transaction.groupby('Date')['Qty'].sum().reset_index()
reg_df['Date'] = pd.to_datetime(reg_df['Date'], format='%d/%m/%Y')
reg_df.sort_values(by='Date', inplace=True)
reg_df.set_index('Date', inplace=True)

# qty SALES IN A YEAR
reg_df.plot(figsize=(12,8), title='Daily Sales', xlabel='Date', ylabel='Total Qty', legend=False)

# SPLIT DATA FOR TRAINING AND TESTING
train = reg_df[:int(0.8*(len(reg_df)))]
test = reg_df[int(0.8*(len(reg_df))):]

# GRID SEARCH (p, d, and q)
auto_arima_model = pm.auto_arima(
    train['Qty'],
    seasonal=False,
    stepwise=False,
    suppress_warnings=True,
    trace = True
)
auto_arima_model.summary()

# IMPORT SARIMAX
p, d, q = auto_arima_model.order
model = SARIMAX(train['Qty'].values, order=(p,d,q))
model_fit = model.fit(disp=False)

# RMSE
from sklearn.metrics import mean_squared_error
predictions = model_fit.predict(start=len(train), end=len(train)+len(test)-1)
rmse = mean_squared_error(test, predictions, squared=False)
rmse

# FORECASTING
period = 90
forecast = model_fit.forecast(steps=period)
index = pd.date_range(start='01-01-2023', periods=period)
df_forecast = pd.DataFrame(forecast, index=index, columns=['Qty'])

plt.figure(figsize=(12,8))
plt.title('Forecasting Sales')
plt.plot(train, label='Train')
plt.plot(test, label='Test')
plt.plot(df_forecast, label='Predicted')
plt.legend(loc='best')
plt.show()

df_forecast.plot(figsize=(12,8), title='Forecasting Sales', xlabel='Date', ylabel='Total Qty', legend=False)

# FORECAST
warnings.filterwarnings('ignore')

product_reg_df = merged_df[['Qty', 'Date', 'Product Name']]
new = product_reg_df.groupby("Product Name")

forecast_product_df = pd.DataFrame({'Date': pd.date_range(start='2023-01-01', periods=90)})

for product_name, group_data in new:
    target_var = group_data['Qty']
    model = SARIMAX(target_var.values, order=(p,d,q))
    model_fit = model.fit(disp=False)
    forecast = model_fit.forecast(90)
    forecast_product_df[product_name] = forecast

forecast_product_df.set_index('Date', inplace=True)
forecast_product_df.head()

# PLOT FORECAST
plt.figure(figsize=(12,8))
for i in forecast_product_df.columns:
    plt.plot(forecast_product_df[i], label=i)
plt.legend(loc=6, bbox_to_anchor=(1,.82))
plt.title('Forecasting Product')
plt.xlabel('Date')
plt.ylabel('Total Qty')
plt.show()

