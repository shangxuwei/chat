import pickle
def register(name, pwd):
    with open('usrs_info.pickle', 'rb') as usr_file:
        exist_usr_info = pickle.load(usr_file)
    # 如果用户名已经在我们的数据文件中
    if name in exist_usr_info:
        return 1
    # 输入无误执行注册
    else:
        exist_usr_info[name] = pwd
        with open('usrs_info.pickle', 'wb') as usr_file:
            pickle.dump(exist_usr_info, usr_file)
        return 2