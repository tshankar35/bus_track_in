'''
This is an Updated Code for Bus Tracking Dashboard
V2.0
Changelogs
1. Added Average Speed and Maximum Speed
2. Logged Max Speed with relevant timestamps
3. Bus Overspeeding History Plot
4. Logged Bus Overspeeding
5. Bus Activity Idle/Running Plot
6. Logs of Running Bus Activity
7. Added Seperate Plots for Latency Logs and Error Latency Logs
8. Revamped the UI
9. Fixed Map Bugs
10. Downloading Logs Directly Now Available!
'''


import json
import statistics as stat
from csv import writer
from datetime import date, datetime
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image
from st_btn_select import st_btn_select
from pytz import timezone
from os.path import exists
import math
from fetcher import fetch_latest, clear

st.set_page_config(layout='wide')
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
col1,col2,col3,col4,col5 = st.columns(5)
with col3:
    image = Image.open("GIET-Logo.png")
    st.image(image,width=150)


st.markdown("<h1 style='padding-left:25%;'>GIET Bus Tracker Dashboard</h1>", unsafe_allow_html=True)
fetch_latest()
clear()
st.markdown("<p style='padding-left:34%;'>"+"Last Fetched at: "+str(datetime.today().astimezone(timezone("Asia/Kolkata")))+"</p>",unsafe_allow_html=True)
st.markdown("#")
st.markdown("#")
if "rerun_button_clicked" not in st.session_state:
    st.session_state.rerun_button_clicked=False

col1,col2 = st.columns(2)
with col1:
    st.header("View By Date")
    pick = st.date_input("Enter Date")
    option = st_btn_select(('Submit','Fetch Latest'))


with col2:
    st.header('Updation Status')
    st.text("Updated Error Log for: "+str(datetime.today().astimezone(timezone("Asia/Kolkata"))))
    st.text("Updated Data Log for: "+str(datetime.today().astimezone(timezone("Asia/Kolkata"))))

st.markdown("#")
st.markdown("#")
if option=='Fetch Latest':
    if exists('log-'+str(date.today())+'.csv'):
        col4,col5 = st.columns(2)
        df_new_data= pd.read_csv('log-'+str(date.today())+'.csv')
        df_new_data = df_new_data.rename(columns={'latitude':'lat','longitude':'long','timestamp':'date'})
        df_new_error = pd.read_csv('errors-'+str(date.today())+'.csv')
        latencylist = list(df_new_error['latency'])
        l = [x for x in latencylist if x>25 and x<30000 and math.isnan(x)==False]
        l1 = [x for x in list(df_new_data['latency']) if x<5 and math.isnan(x)==False]
        with col5:
            st.subheader('Click Below to Save Logs on Your PC')
            st.download_button(label='Download',file_name='log-'+str(pick)+'.csv',data=df_new_data.to_csv().encode('utf-8'))
        with col4:
            st.text("Total Errors Encountered on "+str(pick)+" is "+str(len(l)))
            st.text("All of these errors were recovered successfully!")
    elif st.session_state.rerun_button_clicked:
        st.header("File Absent")
        st.experimental_rerun()
        st.session_state.rerun_button_clicked=True
    option=None
elif option=='Submit' or pick is not None:
    print(str(pick))
    if exists('log-'+str(pick)+'.csv'):
        col4,col5 = st.columns(2)
        df_new_data = pd.read_csv('log-'+str(pick)+'.csv')
        df_new_data = df_new_data.rename(columns={'latitude':'lat','longitude':'long','timestamp':'date'})
        df_new_error = pd.read_csv('errors-'+str(pick)+'.csv')
        latencylist = list(df_new_error['latency'])
        l = [x for x in latencylist if x>25 and x<30000 and math.isnan(x)==False]
        l1 = [x for x in list(df_new_data['latency']) if x<5 and math.isnan(x)==False]
        with col5:
            st.subheader('Click Below to Save The Entire Logs on Your PC')
            st.download_button(label='Download',file_name='log-'+str(pick)+'.csv',data=df_new_data.to_csv().encode('utf-8'))
        with col4:
            st.text("Total Errors Encountered on "+str(pick)+" is "+str(len(l)))
            st.text("All of these errors were recovered successfully!")
    elif st.session_state.rerun_button_clicked:
        st.header("File Absent")
        st.experimental_rerun()
        st.session_state.rerun_button_clicked=True
    option=None
st.header("Bus Travel History")
fig =px.scatter_mapbox(df_new_data,lat='long',lon='lat',hover_name='date',hover_data=['speed'],mapbox_style='dark',zoom=12,center={'lat':19.057435,'lon': 83.824615})
token = 'pk.eyJ1IjoidHNoYW5rYXIzNSIsImEiOiJjbG1qbzZ1bGowNnN2Mmtudm5vNXgxbThoIn0.KGm24u3XtEtsKQPSAA_erA'
fig.update_layout(mapbox_accesstoken=token)
st.plotly_chart(fig)

col1,col2 = st.columns(2)
with col1:
    normalspeed = [x for x in df_new_data['speed'] if x>5 and x<=45 and math.isnan(x)==False]
    m = max([x for x in df_new_data['speed'] if math.isnan(x)==False])
    if len(normalspeed)>0:
        a = sum(normalspeed)/len(normalspeed)
    else:
        a=0
    st.plotly_chart(px.bar(x=[m,a],y=['Max Speed','Average Speed'],title='Average Speed v/s Max Speed',labels={'x':'Speed','y':'Type'}))

with col2:
    st.subheader("Maximum Speed Record")
    st.dataframe(df_new_data[df_new_data['speed']==m],use_container_width=True)
col1,col2 = st.columns(2)
with col1:
    overspeed = [x for x in df_new_data['speed'] if x>45 and math.isnan(x)==False]
    st.plotly_chart(px.pie(values=[len(normalspeed),len(overspeed)],names=['Normal Speed','Overspeed'],hole=0.5,color_discrete_map={'Normal Speed':'green','Overspeed':'orange'},title='Bus Speeding History'))
    st.text("Note: The Vehicle is considered to be overspeeding")
    st.text("if it exceeds the speed of 45kmph.")
with col2:
    st.subheader("Overspeeding Logs")
    st.download_button(label='Download',data=df_new_data[df_new_data['speed']>45].to_csv().encode('utf-8'),file_name='Bus_Overspeeding_Log.csv')
    st.dataframe(df_new_data[df_new_data['speed']>45],use_container_width=True)


st.markdown('#')
st.markdown('#')
st.subheader("A Relative Comparision of Bus Activity")
col1,col2 = st.columns(2)
with col1:
    idletime = [x for x in df_new_data['speed'] if x<5 and math.isnan(x)==False]
    runtim = [x for x in df_new_data['speed'] if x>5 and math.isnan(x)==False]
    st.plotly_chart(px.pie(values=[len(idletime),len(runtim)],names=['Bus Idle','Bus Running'],hole=0.5,color_discrete_map={'Bus Idle':'green','Bus Running':'orange'},title='Bus Activity'))
with col2:
    st.caption("Overall Running Bus Activity Log")
    st.download_button(label='Download',data=df_new_data[df_new_data['speed']>5].to_csv().encode('utf-8'),file_name='Bus_Activity.csv')
    st.dataframe(df_new_data[df_new_data['speed']>5],use_container_width=True)



st.markdown("<h3 style='padding-left:45%;'>Latency</h1>", unsafe_allow_html=True)
col1,col2,col3,col4 = st.columns(4)
with col1:
    st.subheader("Average            :    "+str(np.mean(l1))[:6]+' seconds')
with col4:
    st.subheader("Mode  : "+str(stat.mode(l1))+' seconds')

col1,col2 = st.columns(2)
with col1:
    fig = px.scatter(y=l,labels={'y':'time_delay in sec','x':'reading_count','variable':'difference'},title='Error Latency Graph')
    fig.update_traces(marker=dict(color='red'))
    st.plotly_chart(fig)

with col2:
    latencylist = list(df_new_data['latency'])
    l = [x for x in latencylist if x>25 and x<30000]
    l1 = [x for x in list(df_new_data['latency']) if x<5]
    fig = px.scatter(y=l1,labels={'y':'time_delay in sec','x':'reading_count','variable':'difference'},title='Log Latency Graph')
    fig.update_traces(marker=dict(color='orange'))
    st.plotly_chart(fig)


    

