import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from threading import Thread
import json


class ChatGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.input_Text = tk.Text()
        self.msg = tk.Text()
        self.btn_send = tk.Button()
        self.btn_face = tk.Button()
        self.btn_file = tk.Button()
        self.btn_addfri = tk.Button
        self.chat_list = ttk.Treeview()
        self.chat_page = tk.StringVar()
        self.chat_page.set('public')
        self.fri_list = ''
        self.group_list = ''
        self.run()

    def run(self):
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        width = 1080
        height = 600
        left = (screenWidth - width) / 2
        top = (screenHeight - height) / 2
        self.geometry("%dx%d+%d+%d" % (width, height, left, top))
        self.resizable(width=False, height=False)

        tk.Label(self, textvariable=self.chat_page).place(x=0, y=0)
        tk.Label(self, text="输入").place(x=0, y=435)

        s3 = (tk.Scrollbar(self))
        s3.place(x=775, y=20, height=320)
        self.msg = tk.Text(self, width=110, height=23)
        self.msg.place(x=0, y=30)
        self.msg.configure(state='disabled') #只读不写
        s3.config(command=self.msg.yview)

        self.input_Text = tk.Text(self, width=110, height=4)
        self.input_Text.place(x=0,y=470)

        self.btn_send = tk.Button(self, text="send", bg="lightblue", width=10)
        self.btn_send.place(x=690,y=540)

        self.btn_face = tk.Button(self, text="表情包", width=10)
        self.btn_face.place(x=440,y=435)

        self.btn_file = tk.Button(self, text="文件", width=10)
        self.btn_file.place(x=620,y=435)

        # 添加好友
        self.btn_addfri = tk.Button(self, text="添加好友")
        self.btn_addfri.place(x=990, y=2)

        # 创建树形列表
        s2 = tk.Scrollbar(self)
        s2.place(x=1055,y=30,height=550)
        self.chat_list = ttk.Treeview(self, height=27, show="tree", yscrollcommand=s2.set)
        self.chat_list.place(x=850, y=30)
        s2.config(command=self.chat_list.yview)
        # 好友分组
        self.fri_list = self.chat_list.insert('', 1, 'second', text='好友', )
        self.group_list = self.chat_list.insert('', 2, 'third', text='群聊', )

    def get_msg(self,date: str,user: str,message: str):
        self.msg.configure(state='normal')
        string = f'{date}[{user}]: {message}'
        self.msg.insert(tk.INSERT,string)
        self.msg.configure(state='disabled')

    def clear(self):
        self.msg.configure(state='normal')
        self.msg.delete('1.0', 'end')
        self.msg.configure(state='disabled')

    def get_text_msg(self):
        # chat_model标识了群聊和私聊以及对应目标
        msg = self.input_Text.get('1.0','end')[:-1]
        self.input_Text.delete('1.0','end')
        return msg

    @staticmethod
    def time_out():
        tkinter.messagebox.showerror('Error','连接服务器超时')

    @staticmethod
    def logout():
        tkinter.messagebox.showerror('Error','用户在别处登录')

