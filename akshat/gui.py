from tkinter import *
import re
from tkinter import messagebox
import json
import nltk
import datetime
import webbrowser
import os
import urllib.request
import urllib.parse
import smtplib
import tkinter.simpledialog
from PIL import Image , ImageTk
import pandas as pd
import yaml



from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import random
from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))





def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result







with open("data.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

dataset = pd.read_csv('Book1.csv')
dataset = dataset.set_index("Rollno")
flag = os.O_RDWR
chrome_path = "C:/Users/akshat/AppData/Local/Google/Chrome/Application/chrome.exe"

webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
base = Tk()
base.title("SAVS")
base.geometry("400x470+1100+300")
base.resizable(width=FALSE, height=FALSE)
base.iconbitmap("a.ico")
clearflag=0
a = 0
previousdata=''


record=open('chatlog.txt','a+')
senddetails=open('senddetails.txt','a+')


def doSomething():
    global record,starttime,previousdata
    
    top = Toplevel()
    top.grab_set()

    def cancel():
        top.destroy()
    def later():
        top.destroy()
        base.destroy()
    def submit():
        feedvalue=v1.get()
        feedvalue2=text.get("1.0", 'end-1c')
        if clearflag==0:
            if feedvalue=="average" or feedvalue=="worst" or feedvalue2 != '':
                record.write(starttime)
                record.write("\n")
                record.write(ChatLog.get("1.0", 'end-1c'))
                record.write("\n\nFEEDBACK\n")
                record.write("\n"+feedvalue+"\n\n")
                record.write(feedvalue2)
                record.write("\n\n-------------------------------------------------------------------------------------------\n\n")
                record.close()
        else:
            record.write(starttime)
            record.write("\n")
            record.write(previousdata)
            record.write(ChatLog.get("5.0", 'end-1c'))
            record.write("\nFEEDBACK\n")
            record.write("\n\n" + feedvalue + "\n\n")
            record.write(feedvalue2)
            record.write("\n\n-------------------------------------------------------------------------------------------\n\n")
            record.close()
        top.destroy()
        base.destroy()

    top.title("FEEDBACK FORM")
    top.geometry("550x400+500+200")
    top.resizable(width=FALSE, height=FALSE)
    top.iconbitmap("a.ico")
    label1 = Label(top, text="WE WOULD LIKE YOUR FEEDBACK TO IMPROVE OUR SERVICE", font=("Verdana", 11))
    v1 = StringVar()
    r1 = Radiobutton(top, text='EXCELLENT', variable=v1, value="excellent", font=("Verdana", 11))

    r2 = Radiobutton(top, text='GOOD', variable=v1, value="good", font=("Verdana", 11))
    r3 = Radiobutton(top, text='AVERAGE', variable=v1, value="average", font=("Verdana", 11))

    r4 = Radiobutton(top, text='WORST', variable=v1, value="worst", font=("Verdana", 11))
    v1.set("excellent")
    label2 = Label(top, text="ANY SUGESTION \ COMPLAINT \ COMPLIMENT :- ", font=("Verdana", 11, ))

    text = Text(top, bg="white", bd=3)
    laterButton = Button(top, font=("Verdana", 12, 'bold'), text="LATER", command=later)
    submitButton = Button(top, font=("Verdana", 12, 'bold'), text="SUBMIT", command=submit)
    cancelButton = Button(top, font=("Verdana", 12, 'bold'), text="CANCEL", command=cancel)

    label1.place(x=10, y=20)
    r1.place(x=20, y=60)
    r2.place(x=165, y=60)
    r3.place(x=260, y=60)
    r4.place(x=400, y=60)

    label2.place(x=10, y=120)
    text.place(x=20, y=170, height=150, width=450)
    laterButton.place(x=100, y=330)
    submitButton.place(x=200, y=330)
    cancelButton.place(x=300, y=330)

    top.mainloop()

def wishme():
    ChatLog.insert(END, "Bot: Hello")
    ChatLog.insert(END, "\n\n")
    hour = int(datetime.datetime.now().hour)
    if hour >=0 and hour<=12:
        ChatLog.insert(END,"Bot: Good Morning! ")
    elif hour>=12 and hour <18:
        ChatLog.insert(END,"Bot: Good Aftenoon!")
    else:
        ChatLog.insert(END,"Bot: Good Evening! ")
    ChatLog.insert(END, "\n\n")

ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",wrap=WORD)
ChatLog.config(foreground="#442265", font=("Verdana", 12))


def translate(w):
    global clearflag, previousdata
    w = w.lower()
    if w=="exit":

        doSomething()
        return ""
    if w=="clear":
        clearflag=1
        previousdata=ChatLog.get("1.0", 'end-1c')

        ChatLog.delete("0.0", END)
        wishme()
        return ""
    else:
        ints = predict_class(w, model)
        res = getResponse(ints, intents)
        return res


def send(e):
    global a

    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)
    EntryBox.insert("0.0","")
    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.config(foreground="#442265", font=("Verdana", 12))
        ChatLog.insert(END, "You: " + msg + '\n\n')

        output = translate(msg)
        if type(output) == list:
            for item in output:
                res = item
        else:
            res = output
        if res !='':
            ChatLog.insert(END, "Bot: " + res + '\n\n')
        if a == 0:
            b=button()
            b.firstlayout(1)
            a = 1

     



class button:
    global ChatLog
    textbox1 = Entry(base)
    def firstlayout(self,a):
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "Select your interest to begin with:-")
        ChatLog.insert(END, "\n\n")
        button = Button(base, text="Webpages",command=lambda : self.secondlayout("webpages"))
        ChatLog.window_create(END, window=button )
        button = Button(base, text="SOCIAL SITES", command=lambda : self.secondlayout("social"))
        ChatLog.window_create(END, window=button)
        button = Button(base, text="Information of dit", command=lambda : self.secondlayout("dit"))
        ChatLog.window_create(END, window=button)
        button = Button(base, text="Entertainment", command=lambda : self.secondlayout("entertainment"))
        ChatLog.window_create(END, window=button)
        ChatLog.insert(INSERT, "\n")
        button = Button(base, text="SEND MESSAGE", command=lambda: self.secondlayout("message"))
        ChatLog.window_create(END, window=button)
        button = Button(base, text="GOOGLE SEARCH BAR", command=lambda: self.secondlayout("searchbar"))
        ChatLog.window_create(END, window=button)
        button = Button(base, text="SEND EMAIL", command=lambda: self.secondlayout("email"))
        ChatLog.window_create(END, window=button)
        ChatLog.insert(INSERT, "\n")
        button = Button(base, text="MORE OPTION", command=lambda: self.secondlayout("moreoption"))
        ChatLog.window_create(END, window=button)
        ChatLog.yview(END)
		ChatLog.insert(INSERT, "\n")
    def secondlayout(self,c):
        ChatLog.config(state=NORMAL)
        if(c=="dit"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "DIT UNIVERSITY")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="ABOUT DIT", command=lambda: self.thirdlayout("ditinfo"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="ABOUT CSE BDA", command=lambda: self.secondlayout("bda"))
            ChatLog.window_create(END, window=button1)
        if (c=="bda"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "SELECT DISPLAY OPTION")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="DISPLAY ALL RECORD", command=lambda: self.thirdlayout("ditinfo"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="DISPLAY SINGLE RECORD", command=lambda: self.secondlayout("rollno"))
            ChatLog.window_create(END, window=button1)
        if(c=="rollno"):

            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "ENTER ROLL NUMBER")
            ChatLog.insert(END, "\n\n")
            textbox = Entry(base,bd=5)
            ChatLog.window_create(END, window=textbox)

            button1 = Button(base, text="SEARCH",font=("Verdana", 10, 'bold'),width="7", height=1,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command=lambda: self.displayrecord(rollno=textbox.get()))
            ChatLog.window_create(END, window=button1)
        if(c=="email"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "PLEASE TYPE EMAIL DETAILS HERE")
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "FROM : akshatm214@gmail.con")
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "TO : ")
            textbox = Text(base,bd=3,height="1", width="30")
            ChatLog.window_create(END, window=textbox)
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "MESSAGE \n\n")
            text=Text(base,bd=3,height="7", width="35")
            ChatLog.window_create(END, window=text)
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "                                   ")
            button1 = Button(base, text="SEND",font=("Verdana", 10, 'bold'),width="7", height=1,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command=lambda: self.send(to=textbox.get("1.0", 'end-1c').strip(),content=text.get("1.0", 'end-1c').strip(),type="email"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(END, "\n\n")
        if(c=="message"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "PLEASE TYPE MESSAGE DETAILS HERE")
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "FROM : TEXTLOCAL INTERNET NUMBER")
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "TO : ")
            textbox = Text(base,bd=3,height="1", width="30")
            ChatLog.window_create(END, window=textbox)
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "MESSAGE \n\n")
            text=Text(base,bd=3,height="7", width="35")
            ChatLog.window_create(END, window=text)
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "                                   ")
            button1 = Button(base, text="SEND",font=("Verdana", 10, 'bold'),width="7", height=1,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command=lambda: self.send(to=textbox.get("1.0", 'end-1c').strip(),content=text.get("1.0", 'end-1c').strip(),type="message"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(INSERT, "\n\n")


        if(c=="searchbar"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "GOOGLE SEARCH BAR")
            ChatLog.insert(END, "\n\n")
            self.textbox1 = Entry(base,bd=5)
            ChatLog.window_create(END, window=self.textbox1)

            button1 = Button(base, text="SEARCH",font=("Verdana", 10, 'bold'),width="7", height=1,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command=lambda: self.searchonweb("searchbar"))
            ChatLog.window_create(END, window=button1)

        if(c=="moreoption"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "MORE OPTION  ARE")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="MICROSOFT WORD", command=lambda : self.thirdlayout("word"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="POWERPOINT", command=lambda : self.thirdlayout("ppt"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="NOTEPAD++", command=lambda : self.thirdlayout("notepad++"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="NOTEPAD", command=lambda : self.thirdlayout("notepad"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(END, "\n")
            button = Button(base, text="CODE BLOCKS", command=lambda : self.thirdlayout("codeblocks"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="PYCHARM", command=lambda : self.thirdlayout("pycharm"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="SPYDER", command=lambda : self.thirdlayout("spyder"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="COMMAND PROMPT", command=lambda : self.thirdlayout("cmd"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(END, "\n")

        if(c=="webpages"):
            ChatLog.insert(END, "\n\n")
            ChatLog.insert(END, "WEBPAGES ARE")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="GOOGLE", command=lambda : self.thirdlayout("google"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="YOUTUBE", command=lambda : self.thirdlayout("youtube"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="LMS of dit", command=lambda : self.thirdlayout("lms"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="SAP PORTAL", command=lambda : self.thirdlayout("sap"))
            ChatLog.window_create(END, window=button1)

            ChatLog.insert(END, "\n\n")
        if(c=="entertainment"):
            ChatLog.insert(END, "\n")
            ChatLog.insert(END, "Entertainment LISTS ARE")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="PLAY MUSIC", command=lambda : self.thirdlayout("music"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="VIDEO SONGS", command=lambda : self.thirdlayout("videos"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="GAMES", command=lambda : self.thirdlayout("games"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="YOUTUBER VIDEOS", command=lambda : self.thirdlayout("yvideos"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(END, "\n\n")
        if(c=="social"):
            ChatLog.insert(END, "\n")
            ChatLog.insert(END, "SOCIAL SITES ARE")
            ChatLog.insert(END, "\n\n")
            button = Button(base, text="INSTAGRAM", command=lambda : self.thirdlayout("instagram"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="WHAT'S WEB", command=lambda : self.thirdlayout("whatsweb"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="FACEBOOK", command=lambda : self.thirdlayout("facebook"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="GMAIL", command=lambda : self.thirdlayout("gmail"))
            ChatLog.window_create(END, window=button1)
            ChatLog.insert(END, "\n")
            button = Button(base, text="LINKEDIN", command=lambda : self.thirdlayout("linkedin"))
            ChatLog.window_create(END, window=button)
            button1 = Button(base, text="GITHUB", command=lambda : self.thirdlayout("github"))
            ChatLog.window_create(END, window=button1)
            button = Button(base, text="OUTLOOK", command=lambda : self.thirdlayout("outlook"))
            ChatLog.window_create(END, window=button)
            ChatLog.insert(END, "\n\n")
        ChatLog.yview(END)
    def thirdlayout(self,c):
        try:
            if(c=="google"):
                webbrowser.get('chrome').open_new_tab("google.com")
            if(c=="ditinfo"):
                webbrowser.get('chrome').open_new("https://www.dituniversity.edu.in/")
                webbrowser.get('chrome').open_new("https://www.shiksha.com/university/dit-university-dehradun-25061")
                webbrowser.get('chrome').open_new("https://collegedunia.com/university/13321-dit-university-dit-dehradun/courses-fees")
                webbrowser.get('chrome').open_new("https://collegedunia.com/university/13321-dit-university-dit-dehradun/reviews")
                webbrowser.get('chrome').open_new("https://collegedunia.com/university/13321-dit-university-dit-dehradun/placement")
            if (c=="youtube"):
                webbrowser.get('chrome').open_new_tab("youtube.com")
            if (c=="lms"):
                webbrowser.get('chrome').open_new_tab("lms.dituniversity.edu.in/login/index.php")
            if (c == "sap"):
                webbrowser.get('chrome').open_new_tab("http://webdispatcher.dituniversity.edu.in:8169/irj/portal/anonymous/login")
            if (c == "music"):
                webbrowser.get('chrome').open_new_tab("google.com")
                #os.open('D:/music', flag)
            if (c == "videos"):
                webbrowser.get('chrome').open_new_tab("google.com")
                #os.open('D:/videos', flag)
            if (c == "games"):
                webbrowser.get('chrome').open_new_tab("google.com")
                #os.open('D:/games', flag)
            if (c == "yvideos"):
                #webbrowser.get('chrome').open_new_tab("google.com")
                os.startfile('C:/Users/akshat/Desktop/New folder (6)')
            if(c=="instagram"):
                webbrowser.get('chrome').open_new_tab("https://www.instagram.com/")
            if(c=="whatsweb"):
                webbrowser.get('chrome').open_new_tab("https://web.whatsapp.com/")
            if(c=="facebook"):
                webbrowser.get('chrome').open_new_tab("https://www.facebook.com/")
            if(c=="gmail"):
                webbrowser.get('chrome').open_new_tab("https://accounts.google.com/ServiceLogin")
            if(c=="linkedin"):
                webbrowser.get('chrome').open_new_tab("https://www.linkedin.com/")
            if(c=="github"):
                webbrowser.get('chrome').open_new_tab("https://github.com/")
            if(c=="outlook"):
                webbrowser.get('chrome').open_new_tab("https://outlook.live.com/owa/")
        except Exception as e:
            messagebox.showerror("LOCATION ERROR","BROWSER ISSUE PLEASE CONTACT TO ADMIN ")
            ChatLog.insert(END,"Bot : Browser error")

        try:
            if (c == "word"):
                os.startfile("C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
            if (c == "ppt"):
                os.startfile("C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\POWERPNT.EXE")
            if (c == "notepad++"):
                os.startfile("C:\\Program Files (x86)\\Notepad++\\notepad++.exe")
            if (c == "notepad"):
                os.startfile("C:\\Users\\akshat\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Accessories\\Notepad.lnk")
            if (c == "codeblocks"):
                os.startfile("C:\\Program Files (x86)\\CodeBlocks\\codeblocks.exe")
            if (c == "pycharm"):
                os.startfile("C:\\Program Files\\JetBrains\\PyCharm Community Edition 2020.1\\bin\\pycharm64.exe")
            if (c == "spyder"):
                os.startfile("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Anaconda3 (64-bit)\\Spyder (Anaconda3).lnk")
            if (c == "cmd"):
                os.startfile("C:\\Users\\akshat\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System Tools\\Command Prompt.lnk")
        except Exception as e:
            messagebox.showerror("LOCATION ERROR","LOCATION ISSUE PLEASE CONTACT TO ADMIN ")
            ChatLog.insert(END,"Bot : Location error")
    def searchonweb(self,option):
        if(option=="searchbar"):
            query = self.textbox1.get()
            if query=="":
                messagebox.showerror("ERROR","TYPE SOMETHING!")
            else:
                url = "https://www.google.co.in/search?q=" +(str(query))+ "&oq="+(str(query))+"&gs_l=serp.12..0i71l8.0.0.0.6391.0.0.0.0.0.0.0.0..0.0....0...1c..64.serp..0.0.0.UiQhpfaBsuU"
                webbrowser.get('chrome').open_new_tab(url)
                self.textbox1.delete(0, 'end')

    def send(self,to,content,type):

        ChatLog.config(state=NORMAL)
        code = tkinter.simpledialog.askstring("SECURITY CHECK", "ENTER PASSWORD : ", show='*')
        if code==cfg["code"]:
            senddetails.write(str(datetime.datetime.now()))
            senddetails.write("\n\nTYPE :- "+type+"\n\n")
            senddetails.write("TO  "+to+"                CONTENT :- "+content)
            if type=="email":

                if to.endswith('.com'):
                    try:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.ehlo()
                        server.starttls()
                        server.login(cfg['username'], cfg['password'])
                        server.sendmail('youremail@gmail.com', to, content)
                        server.close()
                        ChatLog.insert(END,"Bot : EMAIL SEND SUCCESSFULLY")
                        senddetails.write("\n\n SEND SUCCESSFULLY ")
                        senddetails.write("\n\n---------------------------------------------------------\n\n")
                    except Exception as e:
                        messagebox.showerror("ERROR","1.PLEASE CHECK YOUR CONNECTION\n2.CHECK YOUR GMAIL ACCOUNT LESS SECURE SETTING\n3.CHECK YOUR EMAIL ID \n4. YOUR ERROR IS  "+str(e))
                        ChatLog.insert(END, "Bot : EMAIL NOT SEND SUCCESSFULLY")
                        senddetails.write("\n\nERROR :- "+str(e))
                        senddetails.write("\n\n---------------------------------------------------------\n\n")
                else:
                    if type=="email":
                        messagebox.showerror("ERROR","CHECK YOUR EMAIL ID")
            if type=="message" and len(to)==10:
                try:
                    data = urllib.parse.urlencode({'apikey': cfg['apikey'], 'numbers': to,
                                                   'message': content})
                    data = data.encode('utf-8')
                    request = urllib.request.Request("https://api.textlocal.in/send/?")
                    f = urllib.request.urlopen(request, data)
                    fr = f.read()
                    #return (fr)
                    ChatLog.insert(END, "Bot : MESSAGE SEND SUCCESSFULLY")
                    senddetails.write("\n\n SEND SUCCESSFULLY ")
                    senddetails.write("\n\n---------------------------------------------------------\n\n")
                except Exception as e:
                    messagebox.showerror("ERROR","1.PLEASE CHECK YOUR CONNECTION\n2.DND SERVICE IS UNAVAILABLE IS COMPULSORY\n3.CHECK YOUR NUMBER \n4. YOUR ERROR IS  " + str(e))
                    ChatLog.insert(INSERT, "Bot : MESSAGE NOT SEND SUCCESSFULLY")
                    senddetails.write("\n\nERROR :- " + str(e))
                    senddetails.write("\n\n---------------------------------------------------------\n\n")
            else:
                if type=="message":
                    messagebox.showerror("ERROR","PLEASE CHECK YOUR NUMBER")
            senddetails.close()
        else:
            messagebox.showerror("CODE ERROR","ENTER VALID CODE")
            ChatLog.insert(END, "Bot : SECURITY ERROR")
            senddetails.write("\n\n SECURITY ERROR ")
            senddetails.write("\n\n---------------------------------------------------------\n\n")
    def displayrecord(self,rollno):
        global photoImg,image1
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "\n\n")
        ChatLog.insert(END, "STUDENT'S DETAILS ARE")
        ChatLog.insert(END, "\n\n")
        rollno=int(rollno)
        sap=str(int(dataset.loc[rollno]['Sap id']))
        email=dataset.loc[rollno]['Email id']
        phoneno=str(int(dataset.loc[rollno]['Phone Number']))
        image1 = Image.open('abc/{}.png'.format(rollno))
        name=dataset.loc[rollno]["Name"]
        rollno = str(int(rollno))
        photoImg = ImageTk.PhotoImage(image1)
        ChatLog.insert(END, "\n\n")
        ChatLog.insert(END, "                        ")
        text1 = Text(base, bd=0, bg="white", height="7", width="10", font="Arial")
        text1.image_create(END, image=photoImg)
        ChatLog.window_create(INSERT, window=text1)
        ChatLog.insert(END, "\n")
        ChatLog.insert(END, "\n")
        ChatLog.insert(END, "   Name:- "+name+"\n\n")
        ChatLog.insert(END, "   Roll Number:- "+rollno+"\n\n")
        ChatLog.insert(END, "   Sap Id:- "+sap+"\n\n")
        ChatLog.insert(END, "   Phone Number:- "+phoneno+"\n\n")
        ChatLog.insert(END, "   Email Id:- "+email+"\n\n")
        ChatLog.config(state=DISABLED)
        text1.config(state=DISABLED)
        ChatLog.yview(END)
image1 = Image.open("z.png")
photoImg = ImageTk.PhotoImage(image1)
# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set
ChatLog.yview(END)
def helpbutton():
    messagebox.showinfo("HELP BOX","1. Use buttons for more accurate result.\n\n"
                                   "2. Use 'OPEN' word to give command (E.g. open youtube).\n\n"
                                   "3. Use 'SEARCH' word to get information (E.g. search ayush).\n\n"
                                   "4. 'CLEAR' word is use to clean initialize the display.\n\n"
                                   "5. 'Exit' word is use to close Assiatant.")

# Create Button to send message
icon=PhotoImage(file = "help.png")
HelpButton = Button(base,image=icon,bd=0,command=helpbutton)
SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Send", width="10", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                    command=lambda :send(e=0))


# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")
EntryBox.bind("<Return>", send)


# Place all components on the screen
scrollbar.place(x=376, y=30, height=382)
HelpButton.place(x=377, y=6, height=24)
ChatLog.place(x=6, y=6, height=406, width=370)
EntryBox.place(x=6, y=420, height=40, width=265)
SendButton.place(x=260, y=420, height=40)
starttime=str(datetime.datetime.now())
wishme()
base.protocol('WM_DELETE_WINDOW', doSomething)
base.mainloop()