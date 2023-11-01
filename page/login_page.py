import tkinter as tk
import tkinter.messagebox

from page import chat_page
from method import client


class LoginGui:
    def __init__(self, init_window_name):
        # 初始化页面配置
        self.tools = client.Client()

        # 页面控件定义
        self.init_window_name = init_window_name
        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('400x300')

        tk.Label(self.init_window_name, text='User name:', font=('Arial', 14)).place(x=10, y=50)
        tk.Label(self.init_window_name, text='Password:', font=('Arial', 14)).place(x=10, y=90)

        self.var_usr_name = tk.StringVar()
        self.entry_usr_name = tk.Entry(self.init_window_name, textvariable=self.var_usr_name, font=('Arial', 14))
        self.entry_usr_name.place(x=120, y=55)

        self.var_usr_pwd = tk.StringVar()
        self.entry_usr_pwd = tk.Entry(self.init_window_name, textvariable=self.var_usr_pwd, font=('Arial', 14), show='*')
        self.entry_usr_pwd.place(x=120, y=95)

        self.btn_login = tk.Button(self.init_window_name, text='Login', command=self.usr_login)
        self.btn_login.place(x=100, y=200)
        self.btn_sign_up = tk.Button(self.init_window_name, text='Sign up', command=self.usr_sign_up)
        self.btn_sign_up.place(x=200, y=200)

    def switch(self,oldwin):
        oldwin.destroy()
        init_window = tk.Tk()
        init_window.resizable(width=False,height=False)
        chat_page.ChatGui(init_window)
        init_window.mainloop()
    #用户登录
    def usr_login(self):
        # 这两行代码就是获取用户输入的usr_name和usr_pwd
        usr_name = self.var_usr_name.get()
        usr_pwd = self.var_usr_pwd.get()
        flag = self.tools.login(usr_name, usr_pwd)

        # 如果用户名和密码与文件中的匹配成功，则会登录成功，并跳出弹窗how are you? 加上你的用户名。
        if flag == 1:
            tkinter.messagebox.showinfo(title='Welcome', message='How are you? ' + usr_name)
            self.switch(self.init_window_name)
            # 如果用户名匹配成功，而密码输入错误，则会弹出'Error, your password is wrong, try again.'
        elif flag == 2:
            tkinter.messagebox.showerror(message='Error, your password is wrong, try again.')



    # 用户注册
    def usr_sign_up(self):
        def sign_to_chat():
        # 以下三行就是获取我们注册时所输入的信息
            pwd = new_pwd.get()
            npf = new_pwd_confirm.get()
            usr = new_name.get()

            # 这里就是判断，如果两次密码输入不一致，则提示Error, Password and confirm password must be the same!
            if pwd != npf:
                tkinter.messagebox.showerror('Error', 'Password and confirm password must be the same!')
            flag = self.tools.register(usr,pwd)
            # 如果用户名已经在我们的数据文件中，则提示Error, The user has already signed up!
            if flag == 1:
                tkinter.messagebox.showerror('Error', 'The user has already signed up!')

            # 最后如果输入无以上错误，则将注册输入的信息记录到文件当中，并提示注册成功Welcome！,You have successfully signed up!，然后销毁窗口。
            elif flag == 2:
                tkinter.messagebox.showinfo('Welcome', 'You have successfully signed up!')
                # 然后销毁窗口。
                window_sign_up.destroy()

        # 定义长在窗口上的窗口
        window_sign_up = tk.Toplevel(self.init_window_name)
        window_sign_up.geometry('300x200')
        window_sign_up.title('Sign up window')

        new_name = tk.StringVar()  # 将输入的注册名赋值给变量
        new_name.set('example@python.com')  # 将最初显示定为'example@python.com'
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
