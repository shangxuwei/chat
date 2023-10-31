import tkinter as tk
from tkinter import ttk

def search():
    #TODO 搜索好友
    pass
class AddGui:
    def __init__(self,init_window_name):
        self.init_window_name=init_window_name
        self.init_window_name.title("添加好友")  # 窗口名
        self.init_window_name.geometry('350x540+10+10')

        self.search_CV =tk.Canvas(self.init_window_name,width=350,height=50,bg='white')
        self.search_CV.place(x=0,y=60)
        self.search_Label = tk.Label(self.init_window_name,text='好友用户名')
        self.search_Label.place(x=5,y=5)
        self.search_Text = tk.Text(self.init_window_name)
        self.search_Text.place(x=80,y=0,height=30,width=200)
        self.search_Button = tk.Button(self.init_window_name,text="搜索",command=search)
        self.search_Button.place(x=300,y=0)

        self.searched_Label = tk.Label(self.init_window_name,text="admin1")
        self.searched_Label.place(x=50,y=75)
        self.searched_Button = tk.Button(self.init_window_name,text='添加好友')
        self.searched_Button.place(x=280,y=70)


        self.requset_Label = tk.Label(self.init_window_name,text='好友请求')
        self.requset_Label.place(x=150,y=150)
        # 创建树形列表
        s1 = tk.Scrollbar(self.init_window_name, ) #s1 滚轮条
        s1.place(x=280, y=175, height=350)
        self.fri_list = ttk.Treeview(self.init_window_name, height=17, show="tree", yscrollcommand=s1.set)
        self.fri_list.place(x=80, y=180)
        s1.config(command=self.fri_list.yview)
        # 好友分组
        self.fri_tree1 = self.fri_list.insert('', 0, 'first', text='admin1', )
        self.fri_tree1_1 = self.fri_list.insert(self.fri_tree1, 0, '001', text='同意', )
        self.fri_tree1_2 = self.fri_list.insert(self.fri_tree1, 1, '002', text='拒绝', )
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='admin2', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, '003', text='同意', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, '004', text='拒绝', )
        self.fri_tree3 = self.fri_list.insert('', 2, 'third', text='admin3', )
        self.fri_tree3_1 = self.fri_list.insert(self.fri_tree3, 0, '005', text='同意', )
        self.fri_tree3_2 = self.fri_list.insert(self.fri_tree3, 1, '006', text='拒绝', )
        def mouse_clicked(event):
            # TODO:接受好友申请
            print(self.fri_list.selection())
        self.fri_list.bind("<Double-Button-1>", mouse_clicked)