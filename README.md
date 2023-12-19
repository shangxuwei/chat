# easy-chat

## 基于python的简单聊天室软件

#### 项目文件结构

```
chat
├── local
│    ├── client.py
│    └── SqliteTools.py
├── page
│    ├── addfriend_page.py
│    ├── chat_page.py
│    ├── file_page.py
│    ├── login_page.py
│    └── register_page.py
├── service
│   ├── serve.py
│   └── SQLTools.py
├── main.py
├── README.md
├── requirements.txt
└── run_service.py
```


#### 运行

本地端在`local/client.py`文件中配置服务器地址及端口

服务端在`service/SQLTools.py`配置数据库账号密码

服务端数据库使用**mysql**或**mariadb**数据库，本地客户端使用**sqlite**数据库，使用时注意相关配置

**TO DO**:

- [x] 用户注册
- [x] 用户登录
- [x] 公共聊天室
- [x] 公共文件传输
- [x] 好友添加
- [x] 好友私聊

