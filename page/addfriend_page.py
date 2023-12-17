import json
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk

class AddGui(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("添加好友")  # 窗口名
        self.geometry('350x540+10+10')
        self.resizable(width=False, height=False)
        self.search_Text = tk.Text()
        self.search_Button = tk.Button()
        self.friend = tk.Label()
        self.group = tk.Label()
        self.addfri_Button = tk.Button()
        self.addgroup_Button = tk.Button()
        self.request_list = ttk.Treeview()
        self.my_fir_request = None
        self.my_group_request = None
        self.friend_tree = None
        self.group_tree = None
        self.run()

    def run(self):
        tk.Label(self,text='好友/群聊名').place(x=5,y=5)

        self.search_Text = tk.Entry(self)
        self.search_Text.place(x=80,y=0,height=30,width=200)

        self.search_Button = tk.Button(self,text="搜索")
        self.search_Button.place(x=300,y=0)

        tk.Canvas(self,width=350,height=50,bg='white').place(x=0,y=60)

        self.friend = tk.Label(self,bg='white')
        self.friend.place(x=50,y=62)
        ttk.Separator(self, orient='horizontal').place(x=0,y=87,width=350)
        self.group = tk.Label(self,bg='white')
        self.group.place(x=50,y=88)

        self.addfri_Button = tk.Button(self,text='添加好友',state='disabled')
        self.addgroup_Button = tk.Button(self,text='添加群聊',state='disabled')
        self.addfri_Button.place(x=280,y=64,height=20)
        self.addgroup_Button.place(x=280,y=90,height=20)


        tk.Label(self,text='好友请求').place(x=150,y=150)

        # 创建树形列表
        self.request_list = ttk.Treeview(self, height=17, show="tree")
        self.request_list.place(x=80, y=180)

        # 好友分组
        my_request_tree = self.request_list.insert('','end','my_request',text='我的请求')
        self.my_fir_request = self.request_list.insert(my_request_tree,'end','my_friend',text='好友')
        self.my_group_request = self.request_list.insert(my_request_tree,'end','my_group',text='群聊')
        self.friend_tree = self.request_list.insert('', 'end', 'friends', text='好友', )
        self.group_tree = self.request_list.insert('', 'end', 'groups', text='群聊', )

        self.request_list.item('friends',open=True)
        self.request_list.item('groups',open=True)

    @staticmethod
    def sent_request(title):
        tkinter.messagebox.showinfo(title,'发送请求成功')
