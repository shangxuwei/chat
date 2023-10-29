from tkinter import *
from tkinter import ttk


class ChatGui:
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name

        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('1080x600+10+10')
        self.init_data_label = Label(self.init_window_name, text="聊天记录")
        self.init_data_label.place(x=0, y=0)
        self.result_data_label = Label(self.init_window_name, text="输入")
        self.result_data_label.place(x=0, y=435)

        self.init_data_Text = Label(self.init_window_name, width=110, height=23, bg="white")
        self.init_data_Text.place(x=0,y=30)
        s1 = Scrollbar(self.init_window_name)
        s1.place(x=775, y=470)
        self.log_data_Text = Text(self.init_window_name, width=110, height=4, yscrollcommand=s1.set)
        s1.config(command=self.log_data_Text.yview)
        self.log_data_Text.place(x=0,y=470)
        self.send_button = Button(self.init_window_name, text="send", bg="lightblue", width=10, )
        self.send_button.place(x=690,y=540)
        self.face_button = Button(self.init_window_name, text="表情包", width=10, )
        self.face_button.place(x=440,y=435)
        self.file_button = Button(self.init_window_name, text="文件", width=10, )
        self.file_button.place(x=620,y=435)

        # 好友按钮
        self.fri_btn = Button(self.init_window_name, text="好友")
        self.fri_btn.place(x=850, y=2)

        # 群按钮
        self.cla_btn = Button(self.init_window_name, text="群聊")
        self.cla_btn.place(x=920, y=2)

        # 添加好友
        self.into_fri_btn = Button(self.init_window_name, text="添加好友")
        self.into_fri_btn.place(x=990, y=2)

        # 创建树形列表
        s2 = Scrollbar(self.init_window_name, )
        s2.place(x=1055,y=30,height=550)
        self.fri_list = ttk.Treeview(self.init_window_name, height=27, show="tree", yscrollcommand=s2.set)
        self.fri_list.place(x=850, y=30)
        s2.config(command=self.fri_list.yview)
        # 好友分组
        self.fri_tree1 = self.fri_list.insert('', 0, 'frist', text='家人', )
        self.fri_tree1_1 = self.fri_list.insert(self.fri_tree1, 0, '001', text='admin1', )
        self.fri_tree1_2 = self.fri_list.insert(self.fri_tree1, 1, '002', text='admin2', )
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='好友', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, 'admin', text='admin3', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, 'testadmin', text='admin4', )
