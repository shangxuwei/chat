# Development documentation



## 1.页面设计（tkinter）

### 1.1 登录页

运行主程序触发

定义变量`var_usr_name`用于保存用户名

定义变量`var_usr_pwd`用于保存密码

```
type:
    var_usr_name : tkinter.StringVar
    var_usr_name : tkinter.StringVar
    
    var.git():
    	tkinter.StringVar -> str
```



按钮`Login`触发登录操作，调用`usr_login`函数

按钮`Sign up`触发注册操作，调用`usr_sign_up`函数



### 1.2 注册页

通过登录页`Sign up`按钮触发

以弹窗形式在登录页上方触发

定义变量`new_name`用于保存用户名

定义变量`new_pwd`用于保存密码

定义变量`new_pwd_confirm`用于保存密码确认值

```
type:
    new_name : tkinter.StringVar
    new_pwd : tkinter.StringVar
    new_pwd_confirm : tkinter.StringVar
    
    var.git():
    	tkinter.StringVar -> str
```

按钮`sign up`触发注册操作，调用函数`sign_to_chat`（内嵌至`usr_sign_up`函数中）



### 1.3 聊天页

登录成功触发





