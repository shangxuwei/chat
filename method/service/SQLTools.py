import time

import pymysql

DBS = {
    'userinfo':{
        'username': 'varchar(33) NOT NULL',
        'password': 'varchar(32) NOT NULL',
        'KEY':['username'],
        'FOREIGN': None
    },
    'groupinfo':{
        'group_name': 'varchar(33) NOT NULL',
        'manager': 'varchar(33) NOT NULL',
        'group_number': 'varchar(33) NOT NULL',
        'KEY': ['group_name'],
        'FOREIGN': 'FOREIGN KEY (manager) REFERENCES userinfo(username),'
                    'FOREIGN KEY (group_number) REFERENCES userinfo(username)'
    },
    'group_chat_history':{
        'id': 'int AUTO_INCREMENT NOT NULL',
        'source_user': 'varchar(33) NOT NULL',
        'target_group': 'varchar(33) NOT NULL',
        'time': 'datetime NOT NULL',
        'content': 'varchar(600) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (source_user) REFERENCES userinfo(username),'
                   'FOREIGN KEY (target_group) REFERENCES groupinfo(group_name)'
    },
    'file':{
        'source_user': 'varchar(33) NOT NULL',
        'time': 'datetime NOT NULL',
        'filecontent': 'longblob NOT NULL',
        'md5': 'varchar(32) NOT NULL',
        'KEY': ['md5'],
        'FOREIGN': 'FOREIGN KEY (source_user) REFERENCES userinfo(username)'
    },
    'file_public':{
        'id': 'int AUTO_INCREMENT NOT NULL',
        'filename': 'varchar(50) NOT NULL',
        'file_hash': 'varchar(32) NOT NULL',
        'downloadable_user': 'varchar(33) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (file_hash) REFERENCES file(md5),'
                   'FOREIGN KEY (downloadable_user) REFERENCES userinfo(username)'
    },
    'friends':{
        'username1': 'varchar(33) NOT NULL NOT NULL',
        'username2': 'varchar(33) NOT NULL',
        'KEY': ['username1','username2'],
        'FOREIGN': 'FOREIGN KEY (username1) REFERENCES userinfo(username),'
                   'FOREIGN KEY (username2) REFERENCES userinfo(username)'
    },
    'private_chat_history':{
        'id': 'int AUTO_INCREMENT NOT NULL',
        'target_user': 'varchar(33) NOT NULL',
        'source_user': 'varchar(33) NOT NULL',
        'time': 'datetime NOT NULL',
        'content': 'varchar(600) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (target_user) REFERENCES userinfo(username),'
                   'FOREIGN KEY (source_user) REFERENCES userinfo(username)'
    }
}
class SQL_Operate:
    def __init__(self):
        # 配置数据库
        mysql_host = 'localhost'
        mysql_port = 3306
        mysql_db = 'easychat'
        mysql_user = 'root'
        mysql_pwd = 'aa123456bb'


        self.conn = pymysql.connect(host=mysql_host,port=mysql_port,user=mysql_user,password=mysql_pwd,charset='utf8mb4')
        self.cur = self.conn.cursor()

        if not bool(self.cur.execute(f"select 1 from information_schema.schemata  where schema_name='{mysql_db}';")):
            self.cur.execute(f'CREATE DATABASE {mysql_db}')
            self.conn=pymysql.connect(host=mysql_host,port=mysql_port,db=mysql_db,
                                      user=mysql_user,password=mysql_pwd,charset='utf8mb4')
            self.cur = self.conn.cursor()
            self.__build()

        self.conn.select_db(mysql_db)
        self.cur = self.conn.cursor()

    def __build(self):
        print("正在初始化数据库")
        for table in DBS:
            sql = f'CREATE TABLE {table} ('
            for field in DBS[table]:
                if field not in ['KEY','FOREIGN']:
                    sql += f'{field} {DBS[table][field]},'
                elif field == 'KEY':
                    keys = ','.join(DBS[table][field])
                    sql += f'PRIMARY KEY ({keys})'
                elif field == 'FOREIGN':
                    if DBS[table][field] is not None:
                        sql += f',{DBS[table][field]}'
            sql += ');'
            self.cur.execute(sql)
            print(sql)
        print("初始化完成")

    def login_check(self,user,pwd):
        sql_select = f'SELECT * FROM userinfo WHERE username="{user}"'
        self.cur.execute(sql_select)
        result = self.cur.fetchall()
        if len(result) == 0 or pwd != result[0][1]:
            return 0
        return 1

    def register(self,user,pwd):
        sql_select = f'SELECT * FROM userinfo WHERE username="{user}"'
        self.cur.execute(sql_select)
        if len(self.cur.fetchall()):
            # user exist
            return 0
        sql_select = f'INSERT INTO userinfo (username,password) VALUES ("{user}","{pwd}")'
        self.cur.execute(sql_select)
        self.conn.commit()
        return 1

    def save_msg(self,date,usr,model,target,msg):
        t = time.localtime(float(date))
        date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        if model:
            sql_select = (f'INSERT INTO private_chat_history (target_user, source_user, time, content)'
                          f' VALUES ("{target}","{usr}","{date}","{msg}")')

        else:
            sql_select = (f'INSERT INTO group_chat_history (target_group, source_user, time, content)'
                          f' VALUES ("{target}","{usr}","{date}","{msg}")')
        self.cur.execute(sql_select)
        self.conn.commit()