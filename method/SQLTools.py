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
        mysql_pwd = ''


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
        
