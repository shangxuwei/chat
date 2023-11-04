from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from page import addfriend_page


class ChatGui:
    def __init__(self, init_window_name, tools):
        self.tools = tools

        self.chat_model = [0,None] # [is私聊,目标]

        self.init_window_name = init_window_name

        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('1080x600+10+10')
        self.init_data_label = Label(self.init_window_name, text="聊天记录")
        self.init_data_label.place(x=0, y=0)
        self.result_data_label = Label(self.init_window_name, text="输入")
        self.result_data_label.place(x=0, y=435)

        s3=Scrollbar(self.init_window_name)
        s3.place(x=775,y=20,height=320)
        self.init_data_Text = Text(self.init_window_name, width=110, height=23)
        self.init_data_Text.place(x=0,y=30)
        self.init_data_Text.configure(state='normal') #可以写
        self.init_data_Text.insert(INSERT, 'Hello, World!\n')
        self.init_data_Text.configure(state='disabled') #只读不写
        s3.config(command=self.init_data_Text.yview)

        self.input_Text = Text(self.init_window_name, width=110, height=4)
        self.input_Text.place(x=0,y=470)

        self.send_button = Button(self.init_window_name, text="send", bg="lightblue", width=10,command=self.send)
        self.send_button.place(x=690,y=540)

        self.face_button = Button(self.init_window_name, text="表情包", width=10, )
        self.face_button.place(x=440,y=435)

        self.file_button = Button(self.init_window_name, text="文件", width=10, )
        self.file_button.place(x=620,y=435)

        # 好友按钮
        self.fri_btn = Label(self.init_window_name, text="好友列表")
        self.fri_btn.place(x=850, y=2)


        # 添加好友
        self.into_fri_btn = Button(self.init_window_name, text="添加好友",command=lambda :self.switch(self.init_window_name))
        self.into_fri_btn.place(x=990, y=2)

        # 创建树形列表
        s2 = Scrollbar(self.init_window_name, )
        s2.place(x=1055,y=30,height=550)
        self.fri_list = ttk.Treeview(self.init_window_name, height=27, show="tree", yscrollcommand=s2.set)
        self.fri_list.place(x=850, y=30)
        s2.config(command=self.fri_list.yview)
        # 好友分组
        self.fri_tree1 = self.fri_list.insert('', 0, 'first', text='家人', )
        self.fri_tree1_1 = self.fri_list.insert(self.fri_tree1, 0, '001', text='admin1', )
        self.fri_tree1_2 = self.fri_list.insert(self.fri_tree1, 1, '002', text='admin2', )
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='好友', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, '003', text='admin3', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, '004', text='admin4', )
        self.fri_tree3 = self.fri_list.insert('', 2, 'third', text='群聊', )
        self.fri_tree3_1 = self.fri_list.insert(self.fri_tree3, 0, '005', text='group1', )
        self.fri_tree3_2 = self.fri_list.insert(self.fri_tree3, 1, '006', text='group2', )

        def mouse_clicked(event):
            # TODO:唤起好友聊天页
            print(self.fri_list.selection())
        self.fri_list.bind("<Double-Button-1>", mouse_clicked)

    def message(self):
        pass

    def send(self):
        msg = str(self.chat_model) + '\n' + self.input_Text.get('1.0','end')[:-1]
        flag = self.tools.chat(msg)
        if not flag:
            tkinter.messagebox.showerror('Error', '连接服务器超时请重试')
        else:
            self.input_Text.delete('1.0','end')

    def switch(self, oldwin):
        init_window = Tk()
        init_window.resizable(width=False, height=False)
        addfriend_page.AddGui(init_window)
        init_window.mainloop()