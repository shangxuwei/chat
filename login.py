from tkinter import *

class MY_GUI():
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name

    def set_init_window(self):
        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('800x600+10+10')
        self.init_data_label = Label(self.init_window_name, text="聊天记录")
        self.init_data_label.grid(row=0, column=0)
        self.result_data_label = Label(self.init_window_name, text="输入")
        self.result_data_label.grid(row=20, column=0)

        self.init_data_Text = Text(self.init_window_name, width=110, height=30)
        self.init_data_Text.grid(row=1, column=0, rowspan=10, columnspan=10)
        self.log_data_Text = Text(self.init_window_name, width=110, height=4)
        self.log_data_Text.grid(row=21, column=0, columnspan=10)

        self.send_button = Button(self.init_window_name, text="send", bg="lightblue", width=10,)
        self.send_button.grid(row=23, column=8,pady=15)
        self.face_button = Button(self.init_window_name, text="表情包", width=10, )
        self.face_button.grid(row=20, column=4,pady=10)
        self.file_button = Button(self.init_window_name, text="文件", width=10, )
        self.file_button.grid(row=20, column=8)

def gui_start():
    init_window = Tk()
    ZMJ_PORTAL = MY_GUI(init_window)
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()


gui_start()