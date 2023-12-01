import sqlite3
import traceback
from typing import Literal

DBS = {
    'message':{
        'id': 'INTEGER',
        'model': 'INT NOT NULL',
        'data': 'DATETIME NOT NULL',
        'page': 'VARCHAR(33) NOT NULL',
        'source': 'VARCHAR(33) NOT NULL',
        'content': 'VARCHAR(600) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': None
    },
    'friends':{
        'username': 'VARCHAR(33) NOT NULL',
        'KEY': ['username'],
        'FOREIGN': None
    },
    'groups':{
        'groupname': 'VARCHAR(33) NOT NULL',
        'KEY': ['groupname'],
        'FOREIGN': None
    },
    'my_friend_requests':{
        'username': 'VARCHAR(33) NOT NULL',
        'KEY': ['username'],
        'FOREIGN': None
    },
    'my_group_requests':{
        'groupname': 'VARCHAR(33) NOT NULL',
        'KEY': ['groupname'],
        'FOREIGN': None
    }
}

class SqlTools:
    """客户端的数据库操作方法集合

    Attributes:
        self.conn: 数据库连接对象
        self.cur: 数据库连接对象游标

    """
    def __init__(self, user, model: Literal['init','run']):
        """初始化类"""
        self.conn = sqlite3.connect(f'./{user}.db')
        self.cur = self.conn.cursor()
        if model == 'init':
            try:
                self.__build()
                self.cur.close()
                self.conn.close()
                print('本地数据库初始化成功')
            except:
                traceback.print_exc()
                print('初始化本地数据库失败')

    def __build(self):
        """初始化本地数据库"""
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

    def save_msg(self, model: int, date: str, page: str, source: str, content: str) -> None:
        """保存聊天消息至本地数据库

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            date: 一个字符串用于表示日期，格式为'%Y-%m-%d %H:%M:%S'
            page: 一个字符串用于关联消息和聊天目标
            source: 一个字符串用于表示消息发送人
            content: 一个字符串表示消息内容

        Returns:
            None
        """
        sql = 'INSERT INTO message (id,model,data,page,source,content) VALUES (?,?,?,?,?,?)'
        self.cur.execute(sql,(None,model,date,page,source,content,))
        self.conn.commit()

    def get_msg(self, model, target) -> list:
        """从数据库中取出对应聊天对象的聊天历史记录

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            target: 一个字符串表示目标用户名

        Returns:
            一个列表保存了对应聊天对象的历史记录
            Examples:
                [(1, 1, '2023-12-01 20:38:33', 'system', 'system', 'Hello World'),....]
        """
        sql = 'SELECT * FROM message WHERE (model=? AND page=?)'
        self.cur.execute(sql,(model,target,))
        msgs = self.cur.fetchall()
        return msgs

    def save_chats(self, model: int, targets:list[str]) -> None:
        """批量保存好友/群聊

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            targets: 一个列表表示目标用户名组

        Returns:
            None
        """
        for _ in targets:
            self.save_chat(model,_)

    def friend_is_exist(self, target: str) -> bool:
        """查看好友是否已存在

        Args:
            target: 一个字符串表示好友名称

        Returns:
            True 好友已存在
            False 好友不存在
        """
        sql = 'SELECT COUNT(username) FROM friends WHERE username=? LIMIT 1'
        self.cur.execute(sql,(target,))
        return bool(self.cur.fetchall()[0][0])

    def group_is_exist(self, target: str) -> bool:
        """查看是否以加入群聊

        Args:
            target: 一个字符串表示群聊名称

        Returns:
            True 已加入群聊
            False 未加入群聊
        """
        sql = 'SELECT COUNT(groupname) FROM groups WHERE groupname=? LIMIT 1'
        self.cur.execute(sql,(target,))
        return bool(self.cur.fetchall()[0][0])

    def save_chat(self,model: int, target: str) -> None:
        """将好友/群聊存入数据库中

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            target: 一个字符串表示目标用户名

        Returns:
            None
        """
        if model:
            if not self.friend_is_exist(target):
                sql = 'INSERT INTO friends (username) VALUES (?)'
                self.cur.execute(sql,(target,))
        else:
            if not self.group_is_exist(target):
                sql = 'INSERT INTO groups (groupname) VALUES (?)'
                self.cur.execute(sql,(target,))
        self.conn.commit()

    def get_chats(self) -> tuple[list[str],list[str]]:
        """从数据库中获取好友和群聊列表

        Returns:
            一个元组，保存了好友和群聊的名称列表
        """
        sql = 'SELECT username FROM friends'
        self.cur.execute(sql)
        friends = self.cur.fetchall()
        sql = 'SELECT groupname FROM groups'
        self.cur.execute(sql)
        groups = self.cur.fetchall()
        return friends,groups

    def save_add_requests(self, model:int, targets: list[str]) -> None:
        """批量保存发起的好友请求至数据库

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            targets: 一个列表，包含目标用户名组

        Returns:
            None
        """
        for _ in targets:
            self.save_add_request(model, _)

    def fir_request_is_exist(self,target: str) -> bool:
        """查看好友请求是否已存在

        Args:
            target: 一个字符串表示目标用户名

        Returns:
            True 好友请求已存在
            False 好友请求不存在
        """
        sql = 'SELECT COUNT(*) FROM my_friend_requests WHERE username=? LIMIT 1'
        self.cur.execute(sql, (target, ))
        return bool(self.cur.fetchall()[0][0])

    def group_request_is_exist(self, target: str) -> bool:
        """查看入群请求是否已存在

        Args:
            target: 一个字符串表示目标群聊

        Returns:
            True 入群请求已存在
            False 入群请求不存在
        """
        sql = 'SELECT COUNT(*) FROM my_group_requests WHERE groupname=? LIMIT 1'
        self.cur.execute(sql, (target,))
        return bool(self.cur.fetchall()[0][0])

    def save_add_request(self, model: int, target: str) -> None:
        """保存用户发起的好友请求

        Args:
            model: 一个整数用于区分群聊和私聊（1为私聊，0为群聊）
            target: 一个字符串表示目标用户名

        Returns:
            None
        """
        if model:
            if not self.group_request_is_exist(target):
                sql = 'INSERT INTO my_friend_requests (username) VALUES (?)'
                self.cur.execute(sql, (target,))
        else:
            if not self.fir_request_is_exist(target):
                sql = 'INSERT INTO my_group_requests (groupname) VALUES (?)'
                self.cur.execute(sql, (target,))
        self.conn.commit()