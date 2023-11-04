# 数据库结构

## web_chat

- userinfo

  | 字段      | 字段类型    | 可否为空 | 备注                    |
  | --------- |-------------| -------- | ----------------------- |
  | username* | varchar(33) | NOT NULL | 用户名                  |
  | password  | varchar(32) | NOT NULL | 密码（使用md5格式存储） |

  
- groupinfo

  | group_name* | varchar(33) | NOT NULL | 群聊名               |
  | ----------- | ----------- | -------- | -------------------- |
  | manager     | varchar



- GROUP_CHAT_HISTORY

  | ID*         | INT          | NOT NULL | 标识ID                                   |
  | ----------- |--------------| -------- | ---------------------------------------- |
  | SOURCE_USER | VARCHAR(33)  | NOT NULL | 消息源用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME     | NOT NULL | 时间戳                                   |
  | CONTENT     | VARCHAR(600) | NOT NULL | 内容                                     |



- GROUP_FILE_HISTORY

  | ID*         | INT         | NOT NULL | 标识ID                                   |
  | ----------- |-------------| -------- | ---------------------------------------- |
  | SOURCE_USER | VARCHAR(33) | NOT NULL | 消息源用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME    | NOT NULL | 时间戳                                   |
  | FILENAME    | VARCHAR(50) | NOT NULL | 文件名                                   |
  | FILECONTENT | LONGBLOB    | NOT NULL | 文件内容                                 |



- FRIENDS

  | USERNAME1* | VARCHAR(33) | NOT NULL | 用户1 |
  | ---------- |-------------| -------- | ----- |
  | USERNAME2* | VARCHAR(33) | NOT NULL | 用户2 |



- HISTORY_PRIVATE_CHAT

  | ID*         | INT          | NOT NULL | 标识ID                                 |
  | ----------- |--------------| -------- | -------------------------------------- |
  | TARGET_USER | VARCHAR(33)  | NOT NULL | 目标用户（与USERINFO中的USERNAME关联） |
  | SOURCE_USER | VARCHAR(33)  | NOT NULL | 发送用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME     | NOT NULL | 时间戳                                 |
  | CONTENT     | VARCHAR(600) | NOT NULL | 内容                                   |

  
