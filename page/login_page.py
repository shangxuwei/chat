import tkinter as tk
from tkinter import ttk
import tkinter.messagebox


class LoginGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.user = tk.StringVar()
        self.pwd = tk.StringVar()
        self.btn_login = ttk.Button()
        self.btn_sign_up = tk.Button()
        self.run()

    def run(self):
        self.title("chat")  # 窗口名
        self.geometry('400x300')
        self.resizable(width=False,height=False)

        ttk.Label(self, text='Username:').place(x=10, y=50)
        ttk.Label(self, text='Password:').place(x=10, y=90)


        ttk.Entry(self, textvariable=self.usr).place(x=120, y=55)
        ttk.Entry(self, textvariable=self.usr, show='*').place(x=120, y=95)


        self.btn_login = tk.Button(self, text='Login', font=('Arial', 14), command=self.usr_login)
        self.btn_login.place(x=100, y=200)
        self.btn_sign_up = tk.Button(self, text='Sign up', font=('Arial', 14), command=self.usr_sign_up)
        self.btn_sign_up.place(x=200, y=200)

    #用户登录
    def login_back(self,flag):
        if flag == 1:
            tkinter.messagebox.showinfo(title='Welcome', message='How are you? ' + usr_name)
            self.destroy()
        elif flag == 0:
            tkinter.messagebox.showerror(message='Error, your password is wrong, try again.')
        elif flag == 2:
            tkinter.messagebox.showerror(message='Error, connect timeout, try again.')



    # 用户注册
    def usr_sign_up(self):
        def sign_to_chat():
        # 以下三行就是获取我们注册时所输入的信息
            pwd = new_pwd.get()
            npf = new_pwd_confirm.get()
            usr = new_name.get()
            if len(usr) >= 10:
                tkinter.messagebox.showerror('Error','用户名过长')
            # 这里就是判断，如果两次密码输入不一致，则提示Error, Password and confirm password must be the same!
            elif pwd != npf:
                tkinter.messagebox.showerror('Error', '两次输入的密码必须相同!')
            else:
                flag = self.tools.register(usr,pwd)
                # 如果用户名已经在我们的数据文件中，则提示Error, The user has already signed up!
                if flag == 0:
                    tkinter.messagebox.showerror('Error', '用户已被注册!')

                # 最后如果输入无以上错误，则将注册输入的信息记录到文件当中，并提示注册成功Welcome！,You have successfully signed up!，然后销毁窗口。
                elif flag == 1:
                    tkinter.messagebox.showinfo('Welcome', '注册成功!')
                    # 然后销毁窗口。
                    window_sign_up.destroy()
                elif flag == 2:
                    tkinter.messagebox.showerror('Error', '连接服务器超时请重试')

        # 定义长在窗口上的窗口
        window_sign_up = tk.Toplevel(self)
        window_sign_up.wm_attributes('-topmost', 1)
        window_sign_up.resizable(width=False, height=False)
        window_sign_up.geometry('300x200')
        window_sign_up.title('Sign up window')

        new_name = tk.StringVar()  # 将输入的注册名赋值给变量
        tk.Label(window_sign_up, text='User name: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
        entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)  # 创建一个注册名的`entry`，变量为`new_name`
        entry_new_name.place(x=130, y=10)  # `entry`放置在坐标（150,10）.

        new_pwd = tk.StringVar()
        tk.Label(window_sign_up, text='Password: ').place(x=10, y=50)
        entry_usr_pwd = tk.Entry(window_sign_up, textvariable=new_pwd, show='*')
        entry_usr_pwd.place(x=130, y=50)

        new_pwd_confirm = tk.StringVar()
        tk.Label(window_sign_up, text='Confirm password: ').place(x=10, y=90)
        entry_usr_pwd_confirm = tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
        entry_usr_pwd_confirm.place(x=130, y=90)

        # 下面的 sign_to_chat
        btn_confirm_sign_up = tk.Button(window_sign_up, text='Sign up', command=sign_to_chat)
        btn_confirm_sign_up.place(x=180, y=120)
