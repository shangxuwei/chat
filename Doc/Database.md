# 数据库结构

## easychat

- userinfo

  | 字段        | 字段类型        | 可否为空     | 备注            | 外键   |
  |-----------|-------------|----------|---------------|------|
  | username* | VARCHAR(33) | NOT NULL | 用户名           | NULL |
  | password  | VARCHAR(32) | NOT NULL | 密码（使用md5格式存储） | NULL |

- groupinfo

  | 字段           | 字段类型        | 可否为空       | 备注    | 外键                 |
  |--------------|-------------|------------|-------|--------------------|
  | group_name*  | VARCHAR(33) | NOT NULL   | 群聊名   | NULL               |
  | manager      | VARCHAR(33) | NOT NULL   | 群聊管理员 | userinfo(username) |
  | group_number | VARCHAR(33) | NOT NULL   | 群成员   | userinfo(username) |



- group_chat_history

  | 字段          | 字段类型               | 可否为空     | 备注    | 外键                 |
  |-------------|--------------------|----------|-------|--------------------|
  | ID*         | INT AUTO_INCREMENT | NOT NULL | 标识ID  | NULL               |
  | SOURCE_USER | VARCHAR(33)        | NOT NULL | 消息源用户 | userinfo(username) |
  | TIME        | DATETIME           | NOT NULL | 时间戳   | NULL               |
  | CONTENT     | VARCHAR(600)       | NOT NULL | 内容    | NULL               |



- file

  | 字段          | 字段类型        | 可否为空     | 备注     | 外键                 |
  |-------------|-------------|----------|--------|--------------------|
  | md5*        | VARCHAR(32) | NOT NULL | 文件md5值 | NULL               |
  | SOURCE_USER | VARCHAR(33) | NOT NULL | 消息源用户  | userinfo(username) |
  | TIME        | DATETIME    | NOT NULL | 时间戳    | NULL               |
  | FILECONTENT | LONGBLOB    | NOT NULL | 文件内容   | NULL               |



- file_public

  | 字段                | 字段类型               | 可否为空     | 备注       | 外键        |
  |-------------------|--------------------|----------|----------|-----------|
  | id*               | INT AUTO_INCREMENT | NOT NULL | 标识id     | NULL      |
  | filename          | VARCHAR(50)        | NOT NULL | 文件名      | NULL      |
  | file_md5          | VARCHAR(32)        | NOT NULL | 文件md5    | file(md5) |
  | downloadable_user | VARCHAR(32)        | NOT NULL | 可下载文件的用户 | NULL      |

  

- friends

  | 字段         | 字段类型        | 可否为空     | 备注  | 外键             |
  |------------|-------------|----------|-----|----------------|
  | username1* | VARCHAR(33) | NOT NULL | 用户1 | userinfo(name) |
  | username2* | VARCHAR(33) | NOT NULL | 用户2 | userinfo(name) |



- private_chat_history

  | 字段          | 字段类型               | 可否为空     | 备注   | 外键                 |
  |-------------|--------------------|----------|------|--------------------|
  | id*         | INT AUTO_INCREMENT | NOT NULL | 标识ID | NULL               |
  | TARGET_USER | VARCHAR(33)        | NOT NULL | 目标用户 | userinfo(username) |
  | SOURCE_USER | VARCHAR(33)        | NOT NULL | 发送用户 | userinfo(username) |
  | TIME        | DATETIME           | NOT NULL | 时间戳  | NULL               |
  | CONTENT     | VARCHAR(600)       | NOT NULL | 内容   | NULL               |
  
  
