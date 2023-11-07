import tkinter as tk
import tkinter.messagebox
class RegisterGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.new_name = tk.StringVar()
        self.new_pwd = tk.StringVar()
        self.new_pwd_confirm = tk.StringVar()
        self.btn_register = tk.Button()
        self.run()

    def run(self):
        self.wm_attributes('-topmost', 1)
        self.protocol("WM_LOSE_FOCUS",self.wm_attributes("-topmost",0))
        screenWidth = self.winfo_screenwidth()  # 获取显示区域的宽度
        screenHeight = self.winfo_screenheight()  # 获取显示区域的高度
        width = 300  # 设定窗口宽度
        height = 200  # 设定窗口高度
        left = (screenWidth - width) / 2
        top = (screenHeight - height) / 2
        self.geometry("%dx%d+%d+%d" % (width, height, left, top))
        self.resizable(width=False, height=False)

        tk.Label(self, text='User name: ').place(x=10, y=10)
        tk.Entry(self, textvariable=self.new_name).place(x=130,y=10)

        tk.Label(self, text='Password: ').place(x=10, y=50)
        tk.Entry(self, textvariable=self.new_pwd, show='*').place(x=130,y=50)

        tk.Label(self, text='Confirm password: ').place(x=10, y=90)
        tk.Entry(self, textvariable=self.new_pwd_confirm, show='*').place(x=130,y=90)

        self.btn_register = tk.Button(self, text='Sign up')
        self.btn_register.place(x=130,y=140)

    @staticmethod
    def user_too_long():
        tkinter.messagebox.showerror('Error', '用户名过长')

    @staticmethod
    def confirm_error():
        tkinter.messagebox.showerror('Error', '两次输入的密码必须相同!')

    @staticmethod
    def user_exist():
        tkinter.messagebox.showerror('Error', '用户已被注册!')


    def succeed(self):
        tkinter.messagebox.showinfo('Welcome', '注册成功!')
        # 然后销毁窗口。
        self.destroy()

    @staticmethod
    def time_out():
        tkinter.messagebox.showerror('Error', '连接服务器超时请重试')