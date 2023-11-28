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
        'username1': 'varchar(33) NOT NULL',
        'username2': 'varchar(33) NOT NULL',
        'KEY': ['username1','username2'],
        'FOREIGN': 'FOREIGN KEY (username1) REFERENCES userinfo(username),'
                   'FOREIGN KEY (username2) REFERENCES userinfo(username)'
    },
    'add_friend_requests':{
        'source':'varchar(33) NOT NULL',
        'target':'varchar(33) NOT NULL',
        'KEY':['source','target'],
        'FOREIGN':'FOREIGN KEY (source) REFERENCES userinfo(username),'
                   'FOREIGN KEY (target) REFERENCES userinfo(username)'
    },
    'add_group_requests': {
        'source': 'varchar(33) NOT NULL',
        'target': 'varchar(33) NOT NULL',
        'KEY': ['source', 'target'],
        'FOREIGN': 'FOREIGN KEY (source) REFERENCES userinfo(username),'
                   'FOREIGN KEY (target) REFERENCES groupinfo(group_name)'
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
    """服务端的数据库操作方法集合

    提供了关于用户注册、登录、消息发送、好友添加查找、好友列表获取等函数
    
    Attributes:
        mysql_host: 数据库运行地址(默认为localhost)
        mysql_port: 数据库运行端口(默认为3306)
        mysql_db: 数据库名称
        mysql_user: 数据库账号(PS:这里仅提供示例账户root不建议实际使用)
        mysql_pwd: 数据库密码(PS:此处仅提供示例建议使用高强度密码)
        System: 聊天程序系统用户
        System_pwd: 聊天程序系统用户密码(以md5格式保存到数据库中)
        conn: 数据库连接对象
        cur: 数据库连接对象游标
    """
    def __init__(self):
        """初始化类对象"""
        mysql_host = 'localhost'
        mysql_port = 3306
        mysql_db = 'easychat'
        mysql_user = 'root'
        mysql_pwd = 'aa123456bb'

        self.System = 'system'
        self.System_pwd = 'aa123456bb'
        self.System_pwd=hashlib.md5(self.System_pwd.encode('utf-8')).hexdigest()


        self.conn = pymysql.connect(host=mysql_host,port=mysql_port,user=mysql_user,password=mysql_pwd,charset='utf8mb4')
        self.cur = self.conn.cursor()

        # 判断数据库是否已经创建 
        if not bool(self.cur.execute("SELECT 1 FROM information_schema.schemata  WHERE schema_name=%s",(mysql_db,))):
            self.cur.execute(f'CREATE DATABASE {mysql_db}')
            self.conn=pymysql.connect(host=mysql_host,port=mysql_port,db=mysql_db,
                                      user=mysql_user,password=mysql_pwd,charset='utf8mb4')
            self.cur = self.conn.cursor()
            self.__build()

        self.conn.select_db(mysql_db)
        self.cur = self.conn.cursor()

    def __build(self):
        """数据库未创建时初始化

        初始化相关表，表结构存储在DBS中
        默认生成用户system,群聊public,管理员为system
        """
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
        sql = 'INSERT INTO userinfo (username,password) VALUES (%s, %s)'
        self.cur.execute(sql,(self.System,self.System_pwd,))
        sql = 'INSERT INTO groupinfo(group_name, manager) VALUES ("public", %s)'
        self.cur.execute(sql,(self.System,))
        sql = 'INSERT INTO group_members (group_name, group_member) VALUES ("public", %s)'
        self.cur.execute(sql,(self.System,))
        self.conn.commit()
        print("初始化完成")


    def login_check(self,user: str,pwd: str) -> int:
        """用户登录校验
        
        将服务端接受到的用户名及密码与数据库中的进行比对返回结果

        Args:
            user: 用户名字符串
            pwd: 密码字符串

        Returns:
            一个整数表示登录校验是否通过
            
            0: 用户登录失败
            1: 用户登录成功
        """
        sql = 'SELECT * FROM userinfo WHERE username=%s'
        self.cur.executemany(sql,(user,))
        result = self.cur.fetchall()
        if len(result) == 0 or pwd != result[0][1]:
            return 0
        return 1

    def register(self,user: str,pwd: str) -> int:
        """用户注册
        
        将服务端收到的注册信息传入，注册用户

        Args:
            user: 用户名字符串
            pwd: 用户密码字符串

        Returns:
            一个整数表示用户是否注册成功

            0: 用户已存在，注册失败
            1: 注册成功
        """
        sql = 'SELECT * FROM userinfo WHERE username=%s'
        self.cur.execute(sql,(user,))
        if len(self.cur.fetchall()):
            # user exist
            return 0
        sql = 'INSERT INTO userinfo (username,password) VALUES (%s, %s)'
        self.cur.execute(sql,(user,pwd,))
        sql = 'INSERT INTO group_members (group_name, group_member) VALUES ("public", %s)'
        self.cur.execute(sql,(user,))
        sql = 'INSERT INTO friends (username1, username2) VALUES (%s,%s)'
        self.cur.execute(sql,('system',user,))
        self.conn.commit()
        return 1

    def save_msg(self,date: float,user: str,model: int,target: str,msg: str) -> None:
        """保存接受到的消息

        Args:
            date: 消息日期时间戳
            user: 发信用户
            model: 是否为群聊标识，1为私聊,0为群聊
            target: 收信目标
            msg: 消息内容

        Returns:
            None
        """
        t = time.localtime(float(date))
        date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        if model:
            sql = ('INSERT INTO private_chat_history (target_user, source_user, time, content)'
                          ' VALUES (%s, %s, %s, %s)')
        else:
            sql = ('INSERT INTO group_chat_history (target_group, source_user, time, content)'
                          ' VALUES (%s, %s, %s, %s)')
        self.cur.execute(sql,(target, user, date, msg,))
        self.conn.commit()

    def get_msg(self,model: int,target: str) -> list:
        """获取指定用户的历史消息

        获取指定用户与其他用户及其在群聊中的历史消息，群聊消息仅获取每个群聊的最后五条，个人不限

        Args:
            model: 获取消息模式标识，1表示私聊，0表示群聊
            target: 目标用户

        Returns:
            返回一个列表包含指定用户的相关历史消息
        """
        if model:
            sql = 'SELECT * FROM private_chat_history WHERE (target_user=%s or source_user=%s)'
            self.cur.execute(sql, (target, target,))
            msgs = list(self.cur.fetchall())
        else:
            msgs = []
            self.cur.execute('SELECT group_name FROM group_members WHERE group_member=%s',(target,))
            groups = self.cur.fetchall()
            for _ in groups:
                sql = 'SELECT * FROM group_chat_history  WHERE target_group=%s'
                self.cur.execute(sql,(_,))
                msgs += list(self.cur.fetchall()[-5:])
        return msgs

    def get_chat_list(self,user: str) -> tuple[list[str],list[str]]:
        """获取指定用户的好友、群聊列表

        Args:
            user: 指定用户

        Returns:
            返回一个元组，其中依次包含了好友列表和群组列表
        """
        sql = 'SELECT username2 FROM friends WHERE username1=%s'
        self.cur.execute(sql,(user,))
        friends = [_[0] for _ in self.cur.fetchall()]
        sql = 'SELECT group_name FROM group_members WHERE group_member=%s'
        self.cur.execute(sql,(user,))
        groups = [_[0] for _ in self.cur.fetchall()]
        return friends,groups

    def get_group_members(self,group: str) -> list:
        """获取一个群聊的所有用户
        
        Args:
            group: 群聊名称

        Returns:
            返回一个列表其中包含了群聊group中的所有成员名称
        """
        sql = 'SELECT group_member FROM group_members WHERE group_name=%s'
        self.cur.execute(sql,(group,))
        members = [_[0] for _ in self.cur.fetchall()]
        return members

    def save_add(self,user: str,model: int,target: str) -> None:
        """将添加好友/群聊请求填入数据库

        Args:
            user: 请求发起人
            model: 标识是否为好友申请，1为好友申请，0为群聊申请
            target: 请求目标

        Returns:
            None
        """
        if model == 1:
            sql = 'SELECT COUNT(*) FROM add_friend_requests WHERE (source=%s AND target=%s) LIMIT 1'
            self.cur.execute(sql,(user,target,))
            is_exist = bool(self.cur.fetchall()[0][0])
            sql = 'SELECT COUNT(*) FROM group_members WHERE (group_name=%s AND group_member=%s) LIMIT 1'
            self.cur.execute(sql,(target,user,))
            is_exist = is_exist and bool(self.cur.fetchall()[0][0])

            if not is_exist:
                sql = 'INSERT INTO add_friend_requests (source, target) VALUES (%s,%s)'
                self.cur.execute(sql,(user,target,))
                self.conn.commit()
        elif model == 0:
            sql = 'SELECT COUNT(*) FROM add_group_requests WHERE (source=%s AND target=%s) LIMIT 1'
            self.cur.execute(sql,(user,target,))
            is_exist = bool(self.cur.fetchall()[0][0])
            if not is_exist:
                sql = 'INSERT INTO add_group_requests (source, target) VALUES (%s,%s)'
                self.cur.execute(sql, (user, target,))
                self.conn.commit()

    def get_add_request(self,user: str) -> list[list[str],list[str],list[str],list[str]]:
        """从数据库中获取指定用户添加好友/入群请求

        Args:
            user: 好友/入群请求发起者，好友请求接收者，群聊管理员

        Returns:
            返回一个列表其中依次包含user发起的好友请求的目标用户id，入群申请目标id，
            向user发起好友请求的用户id，向user为管理员的群聊发起入群请求的用户id
        """
        sql = 'SELECT target FROM add_friend_requests WHERE source=%s'
        self.cur.execute(sql,(user,))
        my_friend_requests = [_[0] for _ in self.cur.fetchall()[-5:]]
        sql = 'SELECT target FROM add_group_requests WHERE source=%s'
        self.cur.execute(sql, (user,))
        my_group_requests = [_[0] for _ in self.cur.fetchall()[-5:]]
        sql = 'SELECT source FROM add_friend_requests WHERE target=%s'
        self.cur.execute(sql,(user,))
        friends = [_[0] for _ in self.cur.fetchall()]
        sql = ('SELECT b.source,target FROM groupinfo a '
                      'JOIN add_group_requests b ON a.group_name = b.target '
                      'WHERE a.manager=%s')
        self.cur.execute(sql,(user,))
        groups = [_ for _ in self.cur.fetchall()]
        return [my_friend_requests,my_group_requests,friends,groups]

    def deal_response(self,model: bool,user: str,target: str,res: int) -> None:
        """处理对好友/入群请求的回复信息进行处理
        
        Args:
            model: 用于标识是否为入群请求，True为入群申请，False为好友申请
            user: 处理信息的用户，即好友申请接收方/群聊管理员
            target: 好友/入群请求发起方
            res: 标识是否接受好友请求

        Returns:
            None
        """
        if model:
            source, group_name = target
            if res:
                sql = 'INSERT INTO group_members (group_name, group_member) VALUES (%s,%s)'
                self.cur.execute(sql,(group_name,source,))
            sql = 'DELETE FROM add_group_requests WHERE (source=%s AND target=%s)'
            self.cur.execute(sql,(source,group_name,))
        else:
            if res:
                sql = 'INSERT INTO friends (username1,username2) VALUES (%s,%s)'
                self.cur.execute(sql,(user,target,))
                self.cur.execute(sql,(target,user,))
            sql = 'DELETE FROM add_friend_requests WHERE (source=%s AND target=%s)'
            self.cur.execute(sql,(target,user))
        self.conn.commit()

    def search(self,target: str) -> tuple[str, str]:
        """搜索用户/群聊
        
        Args:
            target: 目标字符串，群聊名称及用户名称

        Returns:
            返回一个元组包含两个元素，依次为匹配的用户名称，群聊名称，若未找到则对应名称值为None
        """
        sql = 'SELECT username FROM userinfo WHERE username=%s LIMIT 1'
        self.cur.execute(sql,(target,))
        res = self.cur.fetchall()
        user = res[0][0] if len(res)==1 else None
        sql = 'SELECT group_name FROM groupinfo WHERE group_name=%s LIMIT 1'
        self.cur.execute(sql,(target,))
        res = self.cur.fetchall()
        group = res[0][0] if len(res)==1 else None
        return user,group
