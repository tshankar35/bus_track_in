#!/usr/bin/python3
import pandas as pd
import requests
from datetime import datetime,date
from pytz import timezone
from csv import writer

responses = requests.get("http://20.123.74.246:5000/getdata")
responses = responses.json()

df_new = pd.json_normalize(responses,record_path=['log'])
df_new['date'] = df_new['date'].str.replace(',','')
df_new['date'] = pd.to_datetime(df_new['date'])
df_new['long'] = df_new['long'].astype(float)
df_new['lat'] = df_new['lat'].astype(float)

latencylist = [0]
with open('errors-'+str(date.today())+'.csv','w') as f:
	write = writer(f)
	write.writerow(['timestamp','latitude','longitude','speed','latency'])
	f.close()
	pd.to_datetime(df_new['date'])
	d = []
	for i in range(len(df_new.index)-1):
		diff = (df_new['date'][i+1]-df_new['date'][i]).total_seconds()
		latencylist.append(diff)
		if latencylist[i]>10:
			d.append(df_new['date'][i])
			d.append(df_new['lat'][i])
			d.append(df_new['long'][i])
			d.append(df_new['speed'][i])
			d.append(latencylist[i])
			with open('errors-'+str(date.today()),'a') as f:
				write = writer(f)
				write.writerow(d)
				d = []
				f.close()
print("Successfully Written Error Logs")

with open("log-"+str(date.today()+'.csv'),'w') as f:
	write = writer(f)
	write.writerow(['timestamp','latitude','longitude','speed','latency'])
	f.close()
	for i in range(len(df_new.index)):
		d.append(df_new['date'][i])
		d.append(df_new['lat'][i])
		d.append(df_new['long'][i])
		d.append(df_new['speed'][i])
		d.append(latencylist[i])
		with open("log-"+str(date.today())+'.csv,'a') as f:
			write = writer(f)
			write.writerow(d)
			d = []
			f.close()
print("Successfully Written Logs")
responses = requests.get("http://20.123.74.246:5000/clear")
print(responses)
