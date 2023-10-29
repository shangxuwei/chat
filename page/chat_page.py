from tkinter import *
from tkinter import ttk
class MY_GUI():
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name

    def set_init_window(self):
        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('1080x600+10+10')
        self.init_data_label = Label(self.init_window_name, text="聊天记录")
        self.init_data_label.grid(row=0, column=0)
        self.result_data_label = Label(self.init_window_name, text="输入")
        self.result_data_label.grid(row=20, column=0)

        self.init_data_Text = Label(self.init_window_name, width=110, height=23,bg="white")
        self.init_data_Text.grid(row=1, column=0, rowspan=10, columnspan=10)
        self.log_data_Text = Text(self.init_window_name, width=110, height=4)
        self.log_data_Text.grid(row=21, column=0, columnspan=10)

        self.send_button = Button(self.init_window_name, text="send", bg="lightblue", width=10,)
        self.send_button.grid(row=23, column=8,pady=15)
        self.face_button = Button(self.init_window_name, text="表情包", width=10, )
        self.face_button.grid(row=20, column=4,pady=10)
        self.file_button = Button(self.init_window_name, text="文件", width=10, )
        self.file_button.grid(row=20, column=8)

        # self.init_window_name.title("[" + "name" + "] - 聊天界面 ")
        # self.init_window_name.geometry("230x600")
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
        self.fri_list = ttk.Treeview(self.init_window_name, height=27, show="tree")
        self.fri_list.place(x=850, y=30)

        # 好友分组
        self.fri_tree1 = self.fri_list.insert('', 0, 'frist', text='家人', )
        self.fri_tree1_1 = self.fri_list.insert(self.fri_tree1, 0, '001', text='admin1', )
        self.fri_tree1_2 = self.fri_list.insert(self.fri_tree1, 1, '002', text='admin2', )
        self.fri_tree2 = self.fri_list.insert('', 1, 'second', text='好友', )
        self.fri_tree2_1 = self.fri_list.insert(self.fri_tree2, 0, 'admin', text='admin3', )
        self.fri_tree2_2 = self.fri_list.insert(self.fri_tree2, 1, 'testadmin', text='admin4', )
def gui_start():
    init_window = Tk()
    ZMJ_PORTAL = MY_GUI(init_window)
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()


gui_start()