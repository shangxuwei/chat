import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from threading import Thread
import json


class ChatGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.chat_page = [1,"admin"] # [is私聊,目标]
        self.input_Text = tk.Text()
        self.msg = tk.Text()
        self.btn_send = tk.Button()
        self.btn_face = tk.Button()
        self.btn_file = tk.Button()
        self.fri_list = ttk.Treeview()
        self.run()

    def run(self):
        self.init_window_name.title("chat")  # 窗口名
        screenWidth
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        width = 1080
        height = 600
        left = (screenWidth - width) / 2
        top = (screenHeight - height) / 2
        self.geometry("%dx%d+%d+%d" % (width, height, left, top))
        self.resizable(width=False, height=False)

        tk.Label(self.init_window_name, text="聊天记录").place(x=0, y=0)
        tk.Label(self.init_window_name, text="输入").place(x=0, y=435)

        s3 = tk.Scrollbar(self).place(x=775, y=20, height=320)
        self.msg = tk.Text(self, width=110, height=23).place(x=0, y=30)
        self.msg.configure(state='disabled') #只读不写
        s3.config(command=self.msg.yview)

        self.input_Text = tk.Text(self, width=110, height=4)
        self.input_Text.place(x=0,y=470)

        self.btn_send = tk.Button(self, text="send", bg="lightblue", width=10)
        self.btn_send.place(x=690,y=540)

        self.btn_face = tk.Button(self, text="表情包", width=10)
        self.btn_face.place(x=440,y=435)

        self.btn_file = tk.Button(self.init_window_name, text="文件", width=10)
        self.btn_file.place(x=620,y=435)

        # 添加好友
        self.btn_addfri = tk.Button(self, text="添加好友")
        self.btn_addfri.place(x=990, y=2)

        # 创建树形列表
        s2 = Scrollbar(self)
        s2.place(x=1055,y=30,height=550)
        self.fri_list = ttk.Treeview(self.init_window_name, height=27, show="tree", yscrollcommand=s2.set)
        self.fri_list.place(x=850, y=30)
        s2.config(command=self.fri_list.yview)
        # 好友分组
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='好友', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, '003', text='admin3', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, '004', text='admin4', )
        self.fri_tree3 = self.fri_list.insert('', 2, 'third', text='群聊', )
        self.fri_tree3_1 = self.fri_list.insert(self.fri_tree3, 0, '005', text='group1', )
        self.fri_tree3_2 = self.fri_list.insert(self.fri_tree3, 1, '006', text='group2', )

        """bind key
        self.fri_list.bind("<Double-Button-1>", mouse_clicked)
        def mouse_clicked(self,event):
            self.chat_page = 
            print(self.fri_list.selection())

        def entry(event):
            self.send()
            return 'break'
        self.input_Text.bind("<Return>", entry)
        """
    @staticmethod
    def logout():
        tkinter.messagebox.showerror('Error','用户在别处登录')

    @staticmethod
    def time_out():
        tkinter.messagebox.showerror('Error','连接服务器超时')

    def get_msg(self,date,user,message):
        string = f'{date}[{user}]: {message}'
        self.msg.insert(string)

    def get_fri():
        pass

    def clear(self):
        self.msg.configure(state='normal')
        self.msg.delete('1.0', 'end')
        self.msg.configure(state='disable')

    def send(self):
        # chat_model标识了群聊和私聊以及对应目标
        msg = json.dumps(self.chat_page) + '\n' + self.input_Text.get('1.0','end')[:-1]
        self.input_Text.delete('1.0','end')
        return msg
