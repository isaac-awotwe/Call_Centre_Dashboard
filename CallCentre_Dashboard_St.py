# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 21:42:14 2023

@author: isaac.awotwe.z
"""

#Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime, date, time
import seaborn as sns
import matplotlib.pyplot as plt


#Define Functions
def float_to_int(x):
    x_rounded = np.round(x, 0)
    x_int = x_rounded.astype("int")
    return x_int

#Load Data
df_calls = pd.read_excel("Call_Centre_Data.xlsx", sheet_name="Call Data", skiprows=2)


#Engineer data
df_calls["Month"] = df_calls['Call Date'].dt.month
df_calls["Year"] = df_calls['Call Date'].dt.year
df_calls["Month Name"] = pd.Series([d.strftime("%B") for d in df_calls["Call Date"]])

## DataFrame of targets
targets_dict={"metric":["ASA", "RR", "AR", "Satisfaction Rating", "Service Time", "Service Level", "Queue Time", "Talk Time"],
              "value":[35, 0.65, 0.10, 3.2, 60, 0.80, 60, 180]
              }
df_targets=pd.DataFrame(targets_dict)


ASA = 35; RR = 0.65; AR = 0.10; Satisfaction_Rating = 3.2; Service_Time = 60; Service_Level = 0.80; Queue_Time = 60; Talk_Time = 180

## Monthly Metrics
month_nums=[7, 8, 9, 10, 11, 12]
start_date_tiimestamp = df_calls["Call Date"].min()
start_date = date(year=start_date_tiimestamp.year, month=start_date_tiimestamp.month, day=start_date_tiimestamp.day)
dates=pd.date_range(start=start_date, periods=6, freq="M")
dates=[date(2022,7,1), date(2022,8,1), date(2022,9,1), date(2022,10,1), date(2022,11,1), date(2022,12,1)]
df_monthly_metrics = pd.DataFrame({"Date":dates})
df_monthly_metrics["Date"]=pd.to_datetime(df_monthly_metrics["Date"])
df_monthly_metrics["Month Name"] = pd.Series([d.strftime("%B") for d in df_monthly_metrics["Date"]])
df_monthly_metrics["Month"] = df_monthly_metrics["Date"].dt.month
df_monthly_metrics["Year"] = df_monthly_metrics["Date"].dt.year

df_monthly_metrics['Abandon Rate']=pd.Series([df_calls[(df_calls['Month']==month_num) & (df_calls['Agent time']==0)].shape[0]/df_calls[df_calls['Month']==month_num].shape[0] for month_num in month_nums])
#df_monthly_metrics['Abandon rate'] = df_monthly_metrics['Abandon rate'].apply(lambda x: '{:.0%}'.format(x))

df_monthly_metrics['Queue Time'] = pd.Series([df_calls[df_calls['Month']==month_num]['Queue time'].mean() for month_num in month_nums])
df_monthly_metrics['Queue Time'] = df_monthly_metrics['Queue Time'].apply(float_to_int)

df_monthly_metrics['Calls on target']=pd.Series([df_calls[(df_calls['Month']==month_num) & (df_calls['Queue time']<=Queue_Time)].shape[0] for month_num in month_nums])

df_monthly_metrics['IVR Time'] = pd.Series([df_calls[df_calls['Month']==month_num]['IVR time'].mean() for month_num in month_nums])

df_monthly_metrics['Service Level']=pd.Series([df_calls[(df_calls['Month']==month_num) & (df_calls['Queue time']<=Service_Time)].shape[0]/df_calls[df_calls['Month']==month_num].shape[0] for month_num in month_nums])

df_monthly_metrics['Talk Time'] = pd.Series([df_calls[df_calls['Month']==month_num]['Agent time'].sum()/df_calls[df_calls['Month']==month_num].shape[0] for month_num in month_nums])
df_monthly_metrics['Talk Time'] = df_monthly_metrics['Talk Time'].apply(float_to_int)

monthly_calls=[df_calls[df_calls['Month']==month_num].shape[0] for month_num in month_nums]
df_monthly_metrics["Monthly Calls"] = pd.Series(monthly_calls)


## Satisfaction Rates
satisfaction_rates = pd.pivot_table(data=df_calls, values='Satisfaction', index='Agent Name')
satisfaction_rates["Target"] = pd.Series([3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2], index=satisfaction_rates.index)
satisfaction_rates.reset_index(inplace=True)

# Summary Data
start_date = start_date
total_calls = df_calls.shape[0]
average_monthly_calls = df_monthly_metrics["Monthly Calls"].mean()
avg_speed_answer = np.round(df_calls['Queue time'].mean(), 1)
calls_resolved = df_calls[df_calls['Resolved']=='Yes'].shape[0]
calls_abandoned = df_calls[df_calls['Agent time']==0].shape[0]
calls_in_time = df_calls[df_calls['Queue time']<=Service_Time].shape[0]
resolution_rate = calls_resolved/total_calls
service_level_rate = calls_in_time/total_calls
abandon_rate = calls_abandoned/total_calls

df_calls_dec = df_calls[df_calls["Month"]==12]
agent_calls_dec = df_calls_dec.pivot_table(index='Agent Name', columns="Call Date", values="Agent time", aggfunc="sum")
agent_calls_dec.fillna(0, inplace=True)
str_cols=[date.strftime("%Y-%m-%d") for date in agent_calls_dec.columns]
agent_calls_dec.columns=str_cols
agent_calls_dec = agent_calls_dec.apply(float_to_int)
agent_calls_dec.index.name = None


## What metrics will be relevant?
## Difference from baseline
## Percent change by video


#merge daily data with publish data to get delta 

# build dashboard

st.write("### :blue[JPD Call Centre Analysis: July 2022 to December 2022]")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Calls / Month", average_monthly_calls)
with col2:
    delta = (ASA-avg_speed_answer)/avg_speed_answer
    st.metric(label="ASA", value=avg_speed_answer, delta="{:.0%}".format(delta))
with col3:
    delta= (resolution_rate-RR)/RR
    st.metric(label="RR", value="{:.0%}".format(resolution_rate), delta="{:.0%}".format(delta))
with col4:
    delta=(service_level_rate-Service_Level)/Service_Level
    st.metric(label="Service Level", value="{:.0%}".format(service_level_rate), delta="{:.0%}".format(delta))
with col5:
    delta=(abandon_rate-AR)/AR
    st.metric(label="Abandon Rate", value="{:.0%}".format(abandon_rate), delta="{:.0%}".format(delta))



big_col1, big_col2 = st.columns(2, gap = "large")

with big_col1:
    fig = px.bar(data_frame = satisfaction_rates, x='Agent Name', y='Satisfaction')
    fig.add_hline(y=3.2, line_dash = "dash", line_color="orange")
    fig.update_layout({'title':{'text':'Average Agent Satisfaction Rating'}}, width=300, height=300)
    st.plotly_chart(fig)
    
    st.write("##### **Agent Call Times for December 2022**")
    st.dataframe(agent_calls_dec, 600, 310)

with big_col2:
    month_names = tuple(df_monthly_metrics['Month Name'])
    month_select = st.selectbox("## **Select a month to see month-specific metrics**", month_names)
    col6, col7, col8 = st.columns(3)
    with col6:
        metric_name = 'Abandon Rate'
        value = df_monthly_metrics.loc[df_monthly_metrics["Month Name"]==month_select, metric_name].values[0]
        delta = (value-AR)/AR
        st.metric(label = metric_name, value = "{:.0%}".format(value), delta = "{:.0%}".format(delta))

    with col7:
        metric_name = 'Queue Time'
        value = df_monthly_metrics.loc[df_monthly_metrics["Month Name"]==month_select, metric_name].values[0]
        delta = (value-Queue_Time)/Queue_Time
        st.metric(label = "Queue (sec)", value = value, delta = "{:.0%}".format(delta))

    with col8:
        
        metric_name = 'Talk Time'
        value = df_monthly_metrics.loc[df_monthly_metrics["Month Name"]==month_select, metric_name].values[0]
        delta = (value-Talk_Time)/Talk_Time
        st.metric(label = "Talk Time (sec)", value = value, delta = "{:.0%}".format(delta))
    
    
    
    serv_level = df_monthly_metrics.loc[df_monthly_metrics["Month Name"]==month_select, "Service Level"].values[0]
    fig2 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = serv_level,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Service Level"}))
    st.plotly_chart(fig2)
    
    
    df_month_select = df_calls[df_calls['Month Name'] == month_select]
    df_month_select_pivot = df_month_select.pivot_table(index = 'Agent Name', columns = 'Call Date', values = "Call ID", aggfunc = "count")
    df_month_select_pivot = df_month_select_pivot.fillna(0)
    fig3 = go.Figure(data=go.Heatmap(z = df_month_select_pivot.values, y = list(df_month_select_pivot.index), x = df_month_select_pivot.columns, colorscale='Viridis'))
    fig3.update_layout({'title':{'text':'Daily Number of Calls per Agent'}}, width=400, height=400)
    st.plotly_chart(fig3)

