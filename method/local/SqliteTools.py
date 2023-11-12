import sqlite3
import traceback

DBS = {
    'message':{
        'id': 'INT AUTO_INCREMENT NOT NULL',
        'model':'INT NOT NULL',
        'source': 'VARCHAR(33) NOT NULL',
        'content': 'VARCHAR(600) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': None
    }
}
class SqlTools:
    def __init__(self,user):
        self.conn = sqlite3.connect(f'./{user}.db')
        self.cur = self.conn.cursor()
        try:
            self.__build()
        except:
            print('初始化本地数据库失败')

    def __build(self):
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
            print('本地数据库初始化成功')

    def insert_msg(self,model,source,content):
        sql = 'INSERT INTO message (id,model,source,content) VALUES (?,?,?,?)'
        self.cur.execute(sql,(1,model,source,content,))
        print(self.cur.execute('SELECT * FROM message').fetchall())