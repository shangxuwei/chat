import pymysql

DBS = {
    'userinfo':{
        'username': ('varchar(33)',1),
        'password': ('varchar(32)',1),
        'KEY':['username'],
        'FOREIGN': None
    },
    'group_chat_history':{
        'id': ('int',1),
        'source_user': ('varchar(33)',1),
        'time': ('datetime',1),
        'content': ('varchar(600)',1),
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (source_user) REFERENCES userinfo(username)'
    },
    'group_file_history':{
        'id': ('int',1),
        'source_user': ('varchar(33)',1),
        'time': ('datetime',1),
        'filename': ('varchar(50)',1),
        'filecontent': ('longblob',1),
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (source_user) REFERENCES userinfo(username)'
    },
    'friends':{
        'username1': ('varchar(33)',1),
        'username2': ('varchar(33)',1),
        'KEY': ['username1','username2'],
        'FOREIGN': 'FOREIGN KEY (username1) REFERENCES userinfo(username),'
                   'FOREIGN KEY (username2) REFERENCES userinfo(username)'
    },
    'private_chat_history':{
        'id': ('int',1),
        'target_user': ('varchar(33)',1),
        'source_user': ('varchar(33)',1),
        'time': ('datetime',1),
        'content': ('varchar(600)',1),
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

        if not bool(self.cur.execute("select 1 from information_schema.schemata  where schema_name='easychat';")):
            self.cur.execute('CREATE DATABASE easychat')
            self.conn=pymysql.connect(host=mysql_host,port=mysql_port,db='easychat',
                               user=mysql_user,password=mysql_pwd,charset='utf8mb4')
            self.cur = self.conn.cursor()
            self.__build()

    def __build(self):
        for table in DBS:
            print(table)
            sql = f'CREATE TABLE {table} ('
            for field in DBS[table]:
                if field not in ['KEY','FOREIGN']:
                    sql += f'{field} {DBS[table][field][0]}'
                    if DBS[table][field][1]:
                        sql += ' NOT NULL,'
                    else:
                        sql +=','
                elif field == 'KEY':
                    keys = ','.join(DBS[table][field])
                    sql += f'PRIMARY KEY ({keys})'
                elif field == 'FOREIGN':
                    if DBS[table][field] is not None:
                        sql += f',{DBS[table][field]}'
            sql += ');'
            print(sql)
            self.cur.execute(sql)



SQL_obj = SQL_Operate()