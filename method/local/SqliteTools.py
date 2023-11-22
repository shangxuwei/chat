import sqlite3
import traceback

DBS = {
    'message':{
        'id': 'INTEGER',
        'model':'INT NOT NULL',
        'data': 'DATETIME NOT NULL',
        'page': 'VARCHAR(33) NOT NULL',
        'source': 'VARCHAR(33) NOT NULL',
        'content': 'VARCHAR(600) NOT NULL',
        'KEY': ['id'],
        'FOREIGN': None
    }
}
class SqlTools:
    def __init__(self,user,model):
        if model not in ['init','run']:
            raise ValueError('model only accept "init" or "run"')
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

    def insert_msg(self,model,date,page,source,content):
        sql = 'INSERT INTO message (id,model,data,page,source,content) VALUES (?,?,?,?,?,?)'
        self.cur.execute(sql,(None,model,date,page,source,content,))
        self.conn.commit()

    def get_msg(self,model,target):
        sql = 'SELECT * FROM message where page=?'
        self.cur.execute(sql,(target,))
        msgs = self.cur.fetchall()
        return msgs