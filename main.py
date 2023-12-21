import json
import tkinter as tk
import time
from local import client
from page import login_page,register_page,chat_page,addfriend_page,file_page
import os
import windnd
import atexit

@atexit.register
def clean():
    if tools.user is not None:
        tools.sock.sendto(f'LOGOUT\n\n\n\n{tools.user}\n\n'.encode('utf-8'),tools.service)
        time.sleep(0.5)
        try:
            os.remove(f'{tools.user}.db')
        except:
            print(f'删除本地缓存失败，请手动删除 {tools.user}.db 文件')
        try:
            os.remove(f'{tools.user}.db-journal')
        except FileNotFoundError:
            pass
        except:
            print(f'删除本地缓存失败，请手动删除 {tools.user}.db-journal 文件')
    tools.sock.close()

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
            elif flag == 3:
                page_register.invalid_name()

    page_register.btn_register.configure(command=register)
    page_register.mainloop()

def run_chat():
    page_chat = chat_page.ChatGui()
    page_chat.title(f'chat : {tools.user}')

    tools.chat_list = page_chat.chat_list
    tools.chat_fir_list = page_chat.fri_list
    tools.chat_group_list = page_chat.group_list
    tools.messagebox = page_chat.msg
    tools.up_down_task = page_chat.work_task
    tools.message_color_init()

    tools.get_chat_list()
    tools.get_history()

    def entry(event):
        send_msg()
        return 'break'
    page_chat.input_Text.bind("<Return>", entry)

    def enter(event):
        page_chat.input_Text.insert(tk.INSERT,'\n')
        return 'break'
    page_chat.input_Text.bind("<Shift-Return>", enter)

    def drag(files):
        res = page_chat.upload_file(files)
        if res:
            tools.upload(files)
    windnd.hook_dropfiles(page_chat.input_Text,func=drag)

    def mouse_clicked(event):
        try:
            items = page_chat.chat_list.selection()[0]
            values = page_chat.chat_list.item(items)
            model, target = json.loads(values['tags'][0])
            page_chat.chat_page.set(target)
            page_chat.clear()
            tools.switch_chat(model,target)
        except IndexError:
            pass
        except ValueError:
            pass
    page_chat.chat_list.bind("<Double-Button-1>", mouse_clicked)

    def send_msg():
        msg = page_chat.get_text_msg()
        if msg != '':
            tools.chat(msg)
    page_chat.btn_send.configure(command=send_msg)

    def add_friend():
        run_add_page()
    page_chat.btn_addfri.configure(command=add_friend)

    def cat_file_list():
        run_file_page()
    page_chat.btn_file.configure(command=cat_file_list)
    page_chat.mainloop()

def run_file_page():
    page_file = file_page.FileGui()
    tools.file_table = page_file.table
    tools.get_file_list()

    def mouse_clicked(event):
        try:
            items = page_file.table.selection()[0]
            values = page_file.table.item(items)
            if page_file.download_confirm(values['values'][0],values['values'][2]):
                tools.get_download(None,None,values['values'][0],values['values'][2])
        except IndexError:
            pass
    page_file.table.bind("<Double-Button-1>",mouse_clicked)

    page_file.mainloop()

def run_add_page():
    page_add=addfriend_page.AddGui()
    page_add.title(f'添加好友:{tools.user}')
    tools.request_list = page_add.request_list
    tools.my_fri_requests = page_add.my_fir_request
    tools.my_group_requests = page_add.my_group_request
    tools.fri_requests = page_add.friend_tree
    tools.group_requests = page_add.group_tree
    tools.search_text = page_add.search_Text
    tools.res_friend = page_add.friend
    tools.res_group = page_add.group
    tools.add_fri_Btn = page_add.addfri_Button
    tools.add_group_Btn = page_add.addgroup_Button

    tools.get_requests_list()
    def search():
        target = page_add.search_Text.get()
        tools.search(target)
    page_add.search_Button.configure(command=search)

    def add_friend():
        target = page_add.friend.cget("text")
        tools.add_request(1,target)
        page_add.sent_request('添加好友')
        page_add.addfri_Button.configure(state='disabled')
    page_add.addfri_Button.configure(command=add_friend)

    def add_group():
        target = page_add.group.cget("text")
        if page_add.addgroup_Button.cget("text") == '创建群聊':
            tools.new_group(target)
        else:
            tools.add_request(0,target)
            page_add.sent_request('添加群聊')
        page_add.addgroup_Button.configure(state='disabled')
    page_add.addgroup_Button.configure(command=add_group)

    def mouse_clicked(event):
        items = page_add.request_list.selection()[0]
        parent = page_add.request_list.parent(items)
        values = page_add.request_list.item(items)
        try:
            target, res = json.loads(values['tags'][0])
            tools.handle_add_request(target, res)
            tools.request_list.delete(parent)
        except IndexError:
            pass
    page_add.request_list.bind("<Double-Button-1>", mouse_clicked)

    page_add.mainloop()

if __name__ == "__main__":
    try:
        tools = client.Client()
        run_login()
        tools.close_threads_pool()
    except KeyboardInterrupt:
        clean()