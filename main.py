from threading import Thread
import time
from method.local import client
from page import login_page,register_page,chat_page


def run_login():
    page_login = login_page.LoginGui()
    def login():
        flag = tools.login(page_login.user.get(), page_login.pwd.get())
        if flag == 0:
            page_login.pwd_error()
        elif flag == 1:
            page_login.succeed()
            run_chat()
        elif flag == 2:
            page_login.time_out()
    def sign_up():
        # page_login.wm_attributes('-disable',1)
        run_register()

    page_login.btn_login.configure(command=login)
    page_login.btn_sign_up.configure(command=sign_up)
    page_login.mainloop()

def run_register():
    page_register = register_page.RegisterGui()
    def register():
        usr = page_register.user.get()
        pwd = page_register.pwd.get()
        confirm = page_register.pwd_confirm.get()
        if len(usr) >= 10:
            page_register.user_too_long()
        elif pwd != confirm:
            page_register.confirm_error()
        else:
            flag = tools.register(usr, pwd)
            if flag == 0:
                page_register.user_exist()
            elif flag == 1:
                page_register.succeed()
            elif flag == 2:
                page_register.time_out()

    page_register.btn_register.configure(command=register)
    page_register.mainloop()

def run_chat():
    page_chat = chat_page.ChatGui()
    page_chat.title(f'chat : {tools.user}')
    tools.chat_list = page_chat.chat_list
    tools.fir_list = page_chat.fri_list
    tools.group_list = page_chat.group_list
    tools.messagebox = page_chat.msg
    tools.get_chat_list()
    def entry(event):
        send_msg()
        return 'break'
    page_chat.input_Text.bind("<Return>", entry)

    def mouse_clicked(event):
        model, target = page_chat.chat_list.selection()[0].split(' ', 1)
        tools.chat_page = [int(model),target]
        page_chat.chat_page.set(target)
        page_chat.msg.configure(state='normal')
        page_chat.msg.delete('1.0','end')
        page_chat.msg.configure(state='disabled')
    page_chat.chat_list.bind("<Double-Button-1>", mouse_clicked)

    def send_msg():
        tools.chat(page_chat.get_text_msg())
        return 'break'
    page_chat.btn_send.configure(command=send_msg)


    page_chat.mainloop()

if __name__ == "__main__":
    tools = client.Client()
    run_login()



