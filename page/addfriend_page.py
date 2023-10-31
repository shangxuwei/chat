import tkinter as tk


def search():
    #TODO 搜索好友
    pass
class AddGui:
    def __init__(self,init_window_name):
        self.init_window_name=init_window_name

        self.init_window_name.title("添加好友")  # 窗口名
        self.init_window_name.geometry('780x540+10+10')

        self.search_Label = tk.Label(self.init_window_name,text='好友用户名')
        self.search_Label.place(x=10,y=5)
        self.search_Text = tk.Text(self.init_window_name)
        self.search_Text.place(x=80,y=0,height=30)
        self.search_Button = tk.Button(self.init_window_name,text="搜索",command=search)
        self.search_Button.place(x=700,y=0)

