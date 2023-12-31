import streamlit as st
from datetime import datetime
from datetime import date
import requests
import json
import plotly.express as px
import pandas as pd
import numpy as np
from csv import writer
from st_btn_select import st_btn_select
from PIL import Image
import statistics as stat
from pytz import timezone
from os.path import exists
image = Image.open("GIET-Logo.png")
st.set_page_config(layout="wide")
st.image(image,width=150)
st.title ("GIETU Bus-Tracker Dashboard")
responses = requests.get('http://20.123.74.246:5000/getdata')
responses = responses.json()
df_new = pd.json_normalize(responses,record_path=['log'])
df_new['date']=df_new['date'].str.replace(',','')
df_new['date']=pd.to_datetime(df_new['date'])
df_new['long']=df_new['long'].astype(float)
df_new['lat']=df_new['lat'].astype(float)
st.text("Last Fetched at: "+str(datetime.today().astimezone(timezone("Asia/Kolkata"))))
if "rerun_button_clicked" not in st.session_state:
	st.session_state.rerun_button_clicked=False
col1,col2=st.columns(2)
with col1:
    st.header("View By Date")
    pick = st.date_input("Enter Date")
    option=st_btn_select(('Submit','Fetch Latest'))
    
with col2:

    st.header("Updation Status")
    st.text("Updated Error Log For "+str(datetime.today().astimezone(timezone("Asia/Kolkata"))))
    st.text("Updated Data Log For "+str(datetime.today().astimezone(timezone("Asia/Kolkata"))))
latencylist=[0]
with open("errors-"+str(date.today())+".csv",'w') as f:
        write = writer(f)
        write.writerow(['timestamp','latitude','longitude','speed','latency'])
        f.close()
        pd.to_datetime(df_new['date'])
        d=[]
        for i in range(len(df_new.index)-1):
                diff = (df_new['date'][i+1]-df_new['date'][i]).total_seconds()
                latencylist.append(diff)
                if latencylist[i]>10:
                    d.append(df_new['date'][i])
                    d.append(df_new['lat'][i])
                    d.append(df_new['long'][i])
                    d.append(df_new['speed'][i])
                    d.append(latencylist[i])
                    with open("errors-"+str(date.today())+".csv",'a') as f:
                        write = writer(f)
                        write.writerow(d)
                        d=[]
                        f.close()
        

with open("log-"+str(date.today())+".csv",'w') as f:
        write = writer(f)
        write.writerow(['timestamp','latitude','longitude','speed','latency'])
        f.close()
        for i in range(len(df_new.index)):
                d.append(df_new['date'][i])
                d.append(df_new['lat'][i])
                d.append(df_new['long'][i])
                d.append(df_new['speed'][i])
                d.append(latencylist[i])
                with open("log-"+str(date.today())+".csv",'a') as f:
                    write = writer(f)
                    write.writerow(d)
                    d=[]
                    f.close()

if option=="Submit":
    if exists("log-"+str(pick)+".csv"):
        col4,col5 = st.columns(2)
        df_new_data=pd.read_csv("log-"+str(pick)+".csv")
        df_new_data=df_new_data.rename(columns={'latitude':'lat','longitude':'long','timestamp':'date'})
        df_new_error = pd.read_csv("errors-"+str(pick)+".csv")
        latencylist = list(df_new_error['latency'])
        l = [x for x in latencylist if x>25 and x<30000]
        l1 = [x for x in list(df_new_data['latency']) if x<10]
        with col4:
            st.text("Total Errors Encountered on "+str(pick)+" is "+str(len(l)))
            st.text("All of these errors were successfully recovered automatically")
    elif st.session_state.rerun_button_clicked:
       	st.header("File Absent")
       	st.experimental_rerun()
        st.session_state.rerun_button_clicked=True
elif option=="Fetch Latest" and st.session_state.rerun_button_clicked:
    st.experimental_rerun()
    st.session_state.rerun_button_clicked=True

col3,col4 = st.columns(2)
with col3:
    st.header("Bus Travel History")
    if option=="Submit":
        st.header("Date: "+str(pick))
        if exists("log-"+str(pick)+".csv"):
            st.plotly_chart(px.scatter_mapbox(df_new_data,lat='long',lon='lat',hover_name='date',mapbox_style='open-street-map',zoom=6))
        else:
            st.header("N/A")
    else:
        st.header("Date: "+str(date.today()))
        st.plotly_chart(px.scatter_mapbox(df_new,lat='long',lon='lat',hover_name='date',mapbox_style='open-street-map',zoom=5))
    st.header("Number of Days since Last Recharge")
    st.header(list(str(date.today()-date(2022,12,21)).split())[0]+" days")
    st.text("Last Recharge On: 21st December 2022")
with col4:
    st.header("Log Latency Graph")
    if option=="Submit":
        if exists("log-"+str(pick)+".csv"):
            st.plotly_chart(px.scatter(data_frame=df_new_error,y=latencylist,labels={'y':'time_delay in sec','x':'reading_count','variable':'difference'},hover_name='timestamp'))
            st.header("Average Latency: "+str(np.mean(l1)))
            st.header("Most Frequent Latency Value: "+str(stat.mode(l1)))
        else:
            st.header("N/A")
    else:
        st.plotly_chart(px.scatter(data_frame=df_new,y=latencylist,labels={'y':'time_delay in sec','x':'reading_count','variable':'difference'},hover_name='date'))
clear = st.button("Clear Logs from Server?")
if clear:
    responses = requests.get("http://20.123.74.246:5000/clear")
    st.text(responses)



    
