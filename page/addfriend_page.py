import json
import tkinter as tk
from tkinter import ttk

def search():
    #TODO 搜索好友
    pass
class AddGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("添加好友")  # 窗口名
        self.geometry('350x540+10+10')
        self.search_Text = tk.Text()
        self.search_Button = tk.Button()
        self.add_Button = tk.Button()
        self.friend = tk.Label()
        self.group = tk.Label()
        self.addfri_Button = tk.Button()
        self.addgroup_Button = tk.Button()
        self.request_list = ttk.Treeview()
        self.friend_tree = None
        self.group_tree = None
        self.run()

    def run(self):
        tk.Label(self,text='好友用户名').place(x=5,y=5)

        self.search_Text = tk.Text(self)
        self.search_Text.place(x=80,y=0,height=30,width=200)

        self.search_Button = tk.Button(self,text="搜索",command=search)
        self.search_Button.place(x=300,y=0)

        tk.Canvas(self,width=350,height=50,bg='white').place(x=0,y=60)

        self.friend = tk.Label(self,text="admin")
        self.friend.place(x=50,y=62)
        ttk.Separator(self, orient='horizontal').place(x=0,y=87,width=350)
        self.group = tk.Label(self,text="group")
        self.group.place(x=50,y=88)

        self.addfri_Button = tk.Button(self,text='添加好友')
        self.addgroup_Button = tk.Button(self,text='添加群聊')
        self.addfri_Button.place(x=280,y=64,height=20)
        self.addgroup_Button.place(x=280,y=90,height=20)


        tk.Label(self,text='好友请求').place(x=150,y=150)

        # 创建树形列表
        self.request_list = ttk.Treeview(self, height=17, show="tree")
        self.request_list.place(x=80, y=180)

        # 好友分组
        self.friend_tree = self.request_list.insert('', 0, 'friends', text='好友', )
        self.group_tree = self.request_list.insert('', 1, 'groups', text='群聊', )

        self.request_list.item('friends',open=True)
        self.request_list.item('groups',open=True)
        self.request_list.bind("<Double-Button-1>", self.mouse_clicked)
        self.add_requests(['admin'], ['public'])

    def add_requests(self,friends: list[str],groups: list[str]) -> None:
        def add_choice(node: str, target: str) -> None:
            self.request_list.insert(node, 'end', iid=f'{target} 1', text='同意')
            self.request_list.insert(node, 'end', iid=f'{target} 0', text='拒绝')

        for _ in friends:
            friend = self.request_list.insert(self.friend_tree,'end',text=_)
            add_choice(friend,_)
        for _ in groups:
            group = self.request_list.insert(self.group_tree,'end',text=_)
            add_choice(group,_)

    def mouse_clicked(self,event):
        items = self.request_list.selection()[0].split(' ',1)
        print(items)

if __name__ == "__main__":
    page = AddGui()


    page.mainloop()