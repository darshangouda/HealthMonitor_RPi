import Tkinter as tk
import ttk
import tkMessageBox
import random
import urllib2,json
from datetime import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart   # for python 2
from email.MIMEText import MIMEText             # for python 2
import os 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm') 
device_file='/sys/bus/w1/devices/28-041684b221ff/w1_slave'

tempMes=["COLD","NORMAL","FEVER"]
afields=""
std={'date':"",'time':"",'name':"",'id':"",'age':"",'pemail':"",'gemail':"",'temp':float(0.0),'status':""}
combovalue=""
sendFrom,pwd,sendTo= 'PUT_EMAIL_NAME_HERE@gmail.com',"PUT_PASSWORD_HERE",'darshangouda.s.patil@gmail.com' # input email and password
msg = MIMEMultipart('alternative')
msg['Subject'],msg['From'],msg['To']= 'STUDENT MEDICAL DETAILS',sendFrom,sendTo
smtp=""

def read_temp_raw(): #used sensor
    f=open(device_file,'r')
    lines=f.readlines()
    f.close()
    return lines

def read_temp():  #used sensor
    lines=read_temp_raw()
    while lines[0].strip()[-3:]!='YES':
        time.sleep(0.2)
        lines=read_temp_raw()
        equals_pos=lines[1].find('t=')
        if equals_pos!=-1:
            temp_string=lines[1][equals_pos+2:]
            temp_c=float(temp_string)/1000.0
            temp_f=temp_c*9.0/5.0+32.0
            return temp_c # return temepreture in celcius
        
def getData():
    global afields
    try:
        conn=urllib2.urlopen("https://api.thingspeak.com/channels/1468743/feeds.json?api_key=PUT_API_KEY_HERE_FOR_VIEW") #input API Key
        response=conn.read()
        data=json.loads(response)
        afields=data['feeds']
    except:
        tkMessageBox.showerror("ERROR", "READING DATA FROM NETWORK FAILED")
    finally:
        conn.close()
        
def getnames():
    global afields
    names=[]
    for a in afields:
        temp=(a['field1']).encode('utf-8')
        names.append(temp)
    return names

def sendMail():
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(sendFrom,pwd)
    html = "<html><head><style>table{font-family: arial, sans-serif;border-collapse: collapse;width: 100%;}"
    html += "td, th {border: 1px solid #dddddd;text-align: left;padding: 8px;}</style>"
    html += "</head><body><table border=1>"
    html += "<tr><th>DATE</th><td>"+std['date']+"</td></tr><tr><th>TIME</th><td>"+std['time']+"</td></tr>"
    html += "<tr><th>NAME</th><td>"+std['name']+"</td></tr><tr><th>ID</th><td>"+std['id']+"</td></tr>"
    html += "<tr><th>AGE</th><td>"+std['age']+"</td></tr><tr><th>TEPERATURE</th><td>"+str(std['temp'])+"</td></tr>"
    html += "<tr><th>STATUS</th><td>"+std['status']+"</td></tr><tr>"
    phtml =html+ "<th>GUIDE EMAIL</th><td>"+std['gemail']+"</td></tr></table></body></html>"
    msg.attach(MIMEText(phtml, 'html'))
    smtp.sendmail(sendFrom, std['pemail'], msg.as_string())
    ghtml =html+ "<th>PARENT EMAIL</th><td>"+std['pemail']+"</td></tr></table></body></html>"
    msg.attach(MIMEText(ghtml, 'html'))
    smtp.sendmail(sendFrom, std['gemail'], msg.as_string())
    smtp.quit()

def dispDetails(self):
    global combovalue
    std['temp']=float(0.0)
    labeltstatus.config(text = "STATUS:INVALID")
    labeltemp.config(text ="TEMP :"+str(std['temp']))
    combovalue=comboExample.get()
    if(combovalue==''):
        tkMessageBox.showwarning("WARNING", "PLEASE SELECT STUDENT")
    else:
        for a in afields:
            name=str(a['field1'])
            if name == combovalue:
                std['name'],std['id'],std['age'],std['pemail'],std['gemail']=str(a['field1']),str(a['field2']),str(a['field3']),str(a['field4']),str(a['field5'])
        labelname.config(text = "NAME : "+std['name'])
        labelid.config(text = "ID : "+std['id'])
        labelage.config(text = "AGE : "+std['age'])
        labelpemail.config(text = "PARENT EMAIL : "+std['pemail'])
        labelgemail.config(text = "GUIDE EMAIL : "+std['gemail'])

def gettemp():
    global tempstat
    if(combovalue == ""):
        tkMessageBox.showwarning("WARNING", "PLEASE SELECT STUDENT")
    else:
        #std['temp']=read_temp() #reading from sensor
        std['temp']=random.uniform(28.5, 38.5)
        labeltemp.config(text = "TEMP :"+str(std['temp']))
        labeltstatus.config(text = "STATUS:INVALID")
        if std['temp'] <= 30:
            #tkMessageBox.showwarning("INVALID", "INVALID TEMPERATURE VALUE{0}".format(std['temp']))
            std['temp']=float(0.0)
            return
        elif std['temp'] < 36.5:
            std['status']=tempMes[0]
        elif std['temp'] >= 36.5 and 37.5 >= std['temp']:
            std['status']=tempMes[1]
        elif std['temp'] > 37.5:
            std['status']=tempMes[2]
        labeltstatus.config(text = "STATUS:"+std['status'])
        

def updatetemp():
    if(std['temp']==0):
        tkMessageBox.showwarning("WARNING", "INVALID TEMPERATURE VALUE")
        return
    try:
        DTnow=(str(datetime.now()).split('.'))[0]
        std['date']=(DTnow.split(' '))[0]
        std['time']=(DTnow.split(' '))[1]
        urllink="https://api.thingspeak.com/update?api_key=PUT_API_KEY_FOR_UPDATE" #input API Key
        conn=urllib2.urlopen(urllink+"&field1={0}&field2={1}&field3={2}&field4={3}&field5={4}&field6={5}"\
                             .format(std['date'],std['time'],std['name'],std['id'],std['temp'],std['status']))
        sendMail()
        tkMessageBox.showinfo("DONE", "STUDENT TEMPERATURE UPDATED")
    except:
        tkMessageBox.showerror("ERROR", "UPDATING TO NETWORK FAILED")
    finally:
        conn.close()
            
getData()
app = tk.Tk()
app.geometry('450x250')
app.title('STUDENT HEALTH MONITORING SYSTEM')
labelTop = tk.Label(app,text = "Select Student from below")
labelTop.grid(column=0,row=0)
comboExample = ttk.Combobox(app,state = "readonly",values=getnames(),)
comboExample.bind('<<ComboboxSelected>>', dispDetails)
comboExample.grid(column=0, row=1)
#button = tk.Button(app,text = "GET DETAILS",command=dispDetails)
#button.grid(column=1, row=1)
labelname = tk.Label(app,text = "NAME :")
labelname.grid(column=0,row=2)
labelid = tk.Label(app,text = "ID :")
labelid.grid(column=0,row=3)
labelage = tk.Label(app,text = "AGE :")
labelage.grid(column=0,row=4)
labelpemail = tk.Label(app,text = "PARENT EMAIL : ")
labelpemail.grid(column=0,row=5)
labelgemail = tk.Label(app,text = "GUIDE EMAIL : ")
labelgemail.grid(column=0,row=6)
bgetval = tk.Button(app,text = "READ TEMP",command=gettemp)
bgetval.grid(column=0, row=7)
labeltemp = tk.Label(app,text = "TEMP: ")
labeltemp.grid(column=1,row=7)
bupdate = tk.Button(app,text = "UPDATE TEMP",command=updatetemp)
bupdate.grid(column=0, row=8)
labeltstatus = tk.Label(app,text = "STATUS: ")
labeltstatus.grid(column=1,row=8)
app.mainloop()
