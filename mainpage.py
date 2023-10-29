import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.messagebox
import pickle
import loginpage

class MY_GUI():
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name
    # 第2步，给窗口的可视化起名字
    def set_init_window(self):
        self.init_window_name.title("chat")  # 窗口名
        self.init_window_name.geometry('400x300')


        # 第5步，用户信息
        self.init_window_Label=tk.Label(self.init_window_name, text='User name:', font=('Arial', 14)).place(x=10, y=50)
        self.init_window_Label=tk.Label(self.init_window_name, text='Password:', font=('Arial', 14)).place(x=10, y=90)

        # 第6步，用户登录输入框entry
        # 用户名
        self.var_usr_name = tk.StringVar()
        self.var_usr_name.set('example@python.com')
        self.entry_usr_name = tk.Entry(self.init_window_name, textvariable=self.var_usr_name, font=('Arial', 14))
        self.entry_usr_name.place(x=120, y=55)
        # 用户密码
        self.var_usr_pwd = tk.StringVar()
        self.entry_usr_pwd = tk.Entry(self.init_window_name, textvariable=self.var_usr_pwd, font=('Arial', 14), show='*')
        self.entry_usr_pwd.place(x=120, y=95)
        #login按钮
        self.btn_login = tk.Button(self.init_window_name, text='Login', command=self.usr_login)
        self.btn_login.place(x=100, y=200)
        self.btn_sign_up = tk.Button(self.init_window_name, text='Sign up', command=self.usr_sign_up)
        self.btn_sign_up.place(x=200, y=200)
    #第8步，定义用户登录功能
    def usr_login(self):
        # 这两行代码就是获取用户输入的usr_name和usr_pwd
        self.usr_name = self.var_usr_name.get()
        self.usr_pwd = self.var_usr_pwd.get()

        # 这里设置异常捕获，当我们第一次访问用户信息文件时是不存在的，所以这里设置异常捕获。
        # 中间的两行就是我们的匹配，即程序将输入的信息和文件中的信息匹配。
        try:
            with open('usrs_info.pickle', 'rb') as usr_file:
                usrs_info = pickle.load(usr_file)
        except FileNotFoundError:
            # 这里就是我们在没有读取到`usr_file`的时候，程序会创建一个`usr_file`这个文件，并将管理员
            # 的用户和密码写入，即用户名为`admin`密码为`admin`。
            with open('usrs_info.pickle', 'wb') as usr_file:
                usrs_info = {'admin': 'admin'}
                pickle.dump(usrs_info, usr_file)
                usr_file.close()  # 必须先关闭，否则pickle.load()会出现EOFError: Ran out of input

        # 如果用户名和密码与文件中的匹配成功，则会登录成功，并跳出弹窗how are you? 加上你的用户名。
        if self.usr_name in usrs_info:
            if self.usr_pwd == usrs_info[self.usr_name]:
                tkinter.messagebox.showinfo(title='Welcome', message='How are you? ' + self.usr_name)
            # 如果用户名匹配成功，而密码输入错误，则会弹出'Error, your password is wrong, try again.'
            else:
                tkinter.messagebox.showerror(message='Error, your password is wrong, try again.')
        else:  # 如果发现用户名不存在
            is_sign_up = tkinter.messagebox.askyesno('Welcome！ ', 'You have not sign up yet. Sign up now?')
            # 提示需不需要注册新用户
            if is_sign_up:
                self.usr_sign_up()


    # 第9步，定义用户注册功能
    def usr_sign_up(self):
        def sign_to_chat():
        # 以下三行就是获取我们注册时所输入的信息
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get()

            # 这里是打开我们记录数据的文件，将注册信息读出
            with open('usrs_info.pickle', 'rb') as usr_file:
                exist_usr_info = pickle.load(usr_file)
            # 这里就是判断，如果两次密码输入不一致，则提示Error, Password and confirm password must be the same!
            if np != npf:
                tkinter.messagebox.showerror('Error', 'Password and confirm password must be the same!')

            # 如果用户名已经在我们的数据文件中，则提示Error, The user has already signed up!
            elif nn in exist_usr_info:
                tkinter.messagebox.showerror('Error', 'The user has already signed up!')

            # 最后如果输入无以上错误，则将注册输入的信息记录到文件当中，并提示注册成功Welcome！,You have successfully signed up!，然后销毁窗口。
            else:
                exist_usr_info[nn] = np
                with open('usrs_info.pickle', 'wb') as usr_file:
                    pickle.dump(exist_usr_info, usr_file)
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
        btn_comfirm_sign_up = tk.Button(window_sign_up, text='Sign up', command=sign_to_chat)
        btn_comfirm_sign_up.place(x=180, y=120)


def gui_start():
    init_window = tk.Tk()
    ZMJ_PORTAL = MY_GUI(init_window)
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()


gui_start()

