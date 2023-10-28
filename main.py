from tkinter import *

class MY_GUI():
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name

    def set_init_window(self):
        self.init_window_name.title("聊天软件")  # 窗口名
        self.init_window_name.geometry('420x100+10+10')
        self.init_data_label = Label(self.init_window_name, text="账户")
        self.init_data_label.grid(row=0, column=0)
        self.result_data_label = Label(self.init_window_name, text="密码")
        self.result_data_label.grid(row=20, column=0)

        self.init_data_Text = Text(self.init_window_name, width=50, height=2)
        self.init_data_Text.grid(row=0, column=2, rowspan=10, columnspan=10)
        self.log_data_Text = Text(self.init_window_name, width=50, height=2)
        self.log_data_Text.grid(row=20, column=2, columnspan=10)

        self.send_button = Button(self.init_window_name, text="登录", width=10,command=self.set_init_window2)
        self.send_button.grid(row=30, column=2)
        self.send_button = Button(self.init_window_name, text="注册", width=10, )
        self.send_button.grid(row=30, column=6)

    def set_init_window2(self):
        self.init_window_name.title("聊天软件")
        self.init_window_name.geometry('1068x681+10+10')
        self.init_data_label = Label(self.init_window_name, text="聊天记录")
        self.init_data_label.grid(row=0, column=0)
        self.result_data_label = Label(self.init_window_name, text="输入")
        self.result_data_label.grid(row=12, column=0)

        self.init_data_Text = Text(self.init_window_name, width=150, height=35)
        self.init_data_Text.grid(row=1, column=0, rowspan=10, columnspan=10)
        self.log_data_Text = Text(self.init_window_name, width=150, height=5)
        self.log_data_Text.grid(row=13, column=0, columnspan=10)

        self.send_button = Button(self.init_window_name, text="send", bg="lightblue", width=10,)
        self.send_button.grid(row=18, column=4)
        self.send_button = Button(self.init_window_name, text="表情包", width=10, )
        self.send_button.grid(row=12, column=4)
        self.send_button = Button(self.init_window_name, text="文件", width=10, )
        self.send_button.grid(row=12, column=8)

def gui_start():
    init_window = Tk()
    ZMJ_PORTAL = MY_GUI(init_window)
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()


gui_start()