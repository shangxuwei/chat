import tkinter as tk
from tkinter import ttk


class MY_GUI:
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name

        self.init_window_name.title("[" + "name" + "] - 聊天界面 ")
        self.init_window_name.geometry("230x600")
        # 好友按钮
        self.fri_btn = tk.Button(self.init_window_name, text="好友")
        self.fri_btn.place(x=10, y=2)

        # 群按钮
        self.cla_btn = tk.Button(self.init_window_name, text="群聊")
        self.cla_btn.place(x=70, y=2)

        # 添加好友
        self.into_fri_btn = tk.Button(self.init_window_name, text="添加好友")
        self.into_fri_btn.place(x=130, y=2)

        # 创建树形列表
        self.fri_list = ttk.Treeview(self.init_window_name, height=27, show="tree")
        self.fri_list.place(x=10, y=30)

        # 好友分组
        self.fri_tree1 = self.fri_list.insert('', 0, 'frist', text='家人', )
        self.fri_tree1_1 = self.fri_list.insert(self.fri_tree1, 0, '001', text='admin1', )
        self.fri_tree1_2 = self.fri_list.insert(self.fri_tree1, 1, '002', text='admin2', )
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='好友', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, 'admin', text='admin3', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, 'testadmin', text='admin4', )

