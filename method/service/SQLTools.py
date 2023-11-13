import time
import hashlib
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
        'KEY': ['group_name'],
        'FOREIGN': 'FOREIGN KEY (manager) REFERENCES userinfo(username)'
    },
    'group_members':{
        'id': 'int AUTO_INCREMENT NOT NULL',
        'group_name': 'varchar(33) NOT NULL',
        'group_member': 'varchar(33) NOT NULL',
        'KEY': ['id'],
        'FOREIGN' : 'FOREIGN KEY (group_name) REFERENCES groupinfo(group_name),'
                    'FOREIGN KEY (group_member) REFERENCES userinfo(username)'
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
        'file_md5': 'varchar(32) NOT NULL',
        'downloadable_user': 'varchar(33) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': 'FOREIGN KEY (file_md5) REFERENCES file(md5),'
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

        self.admin_user = 'admin'
        self.admin_pwd = 'admin'


        self.conn = pymysql.connect(host=mysql_host,port=mysql_port,user=mysql_user,password=mysql_pwd,charset='utf8mb4')
        self.cur = self.conn.cursor()

        if not bool(self.cur.execute("select 1 from information_schema.schemata  where schema_name=%s",(mysql_db,))):
            self.cur.execute('CREATE DATABASE %s', (mysql_db,))
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
            print(f'初始化{table}表')
        print("初始化完成")
        pwd = hashlib.md5(self.admin_pwd.encode('utf-8')).hexdigest()
        sql_select = 'INSERT INTO userinfo (username,password) VALUES (%s, %s)'
        self.cur.execute(sql_select,(self.admin_user,self.admin_pwd,))
        sql_select = 'INSERT INTO groupinfo(group_name, manager) VALUES ("public", %s)'
        self.cur.execute(sql_select,(self.admin_user,))
        sql_select = 'INSERT INTO group_members (group_name, group_member) VALUES ("public", %s)'
        self.cur.execute(sql_select,(self.admin_user,))
        self.conn.commit()


    def login_check(self,user,pwd):
        sql_select = 'SELECT * FROM userinfo WHERE username=%s'
        self.cur.executemany(sql_select,(user,))
        result = self.cur.fetchall()
        if len(result) == 0 or pwd != result[0][1]:
            return 0
        return 1

    def register(self,user,pwd):
        sql_select = 'SELECT * FROM userinfo WHERE username=%s'
        self.cur.execute(sql_select,(user,))
        if len(self.cur.fetchall()):
            # user exist
            return 0
        sql_select = 'INSERT INTO userinfo (username,password) VALUES (%s, %s)'
        self.cur.execute(sql_select,(user,pwd,))
        sql_select = 'INSERT INTO group_members (group_name, group_member) VALUES ("public", %s)'
        self.cur.execute(sql_select,(user,))
        self.conn.commit()
        return 1

    def save_msg(self,date,user,model,target,msg):
        t = time.localtime(float(date))
        date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        if model:
            sql_select = ('INSERT INTO private_chat_history (target_user, source_user, time, content)'
                          ' VALUES (%s, %s, %s, %s)')
        else:
            sql_select = ('INSERT INTO group_chat_history (target_group, source_user, time, content)'
                          ' VALUES (%s, %s, %s, %s)')
        self.cur.execute(sql_select,(target, user, date, msg,))
        self.conn.commit()

    def get_msg(self,model,target):
        if model:
            sql_select = 'SELECT * FROM private_chat_history where (target_user=%s or source_user=%s)'
            self.cur.execute(sql_select, (target, target,))
            msgs = list(self.cur.fetchall())
        else:
            msgs = []
            self.cur.execute('SELECT group_name FROM group_members WHERE group_member=%s',(target,))
            groups = self.cur.fetchall()
            for _ in groups:
                sql_select = 'SELECT * FROM group_chat_history  where target_group=%s'
                self.cur.execute(sql_select,(_,))
                msgs += list(self.cur.fetchall()[-5:])
        return msgs

    def get_chat_list(self,user):
        sql_select = 'SELECT username2 FROM friends where username1=%s'
        self.cur.execute(sql_select,(user,))
        friends = [_[0] for _ in self.cur.fetchall()]
        sql_select = 'SELECT group_name FROM group_members where group_member=%s'
        self.cur.execute(sql_select,(user,))
        groups = [_[0] for _ in self.cur.fetchall()]
        return friends,groups

    def get_group_members(self,group):
        sql_select = f'SELECT group_member FROM group_members where group_name=%s'
        self.cur.execute(sql_select,(group,))
        members = [_[0] for _ in self.cur.fetchall()]
        return members