import pickle
def register(name, pwd):
    with open('usrs_info.pickle', 'rb') as usr_file:
        exist_usr_info = pickle.load(usr_file)
    # 这里就是判断，如果两次密码输入不一致，则提示Error, Password and confirm password must be the same!


    # 如果用户名已经在我们的数据文件中，则提示Error, The user has already signed up!
    if name in exist_usr_info:
        return 1

    # 最后如果输入无以上错误，则将注册输入的信息记录到文件当中，并提示注册成功Welcome！,You have successfully signed up!，然后销毁窗口。
    else:
        exist_usr_info[name] = pwd
        with open('usrs_info.pickle', 'wb') as usr_file:
            pickle.dump(exist_usr_info, usr_file)
        return 2