# 一、数据库结构

## web_chat

- USERINFO

  | *USERNAME | TEXT | NOT NULL | 用户名 |
  | --------- | ---- | -------- | ------ |
  | PASSWORD  | TEXT | NOT NULL | 密码   |

  

- GROUP_CHAT_HISTORY

  | *ID         | TEXT     | NOT NULL | 标识ID                                   |
  | ----------- | -------- | -------- | ---------------------------------------- |
  | SOURCE_USER | TEXT     | NOT NULL | 消息源用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME | NOT NULL | 时间戳                                   |
  | CONTENT     | TEXT     | NOT NULL | 内容                                     |



- GROUP_FILE_HISTORY

  | *ID         | TEXT     | NOT NULL | 标识ID                                   |
  | ----------- | -------- | -------- | ---------------------------------------- |
  | SOURCE_USER | TEXT     | NOT NULL | 消息源用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME | NOT NULL | 时间戳                                   |
  | FILENAME    | TEXT     | NOT NULL | 文件名                                   |
  | FILECONTENT | TEXT     | NOT NULL | 文件内容                                 |



- FRIENDS

  | USERNAME1* | TEXT | NOT NULL | 用户1 |
  | ---------- | ---- | -------- | ----- |
  | USERNAME2* | TEXT | NOT NULL | 用户2 |



- HISTORY_PRIVATE_CHAT

  | *ID         | INTEGER  | NOT NULL | 标识ID                                 |
  | ----------- | -------- | -------- | -------------------------------------- |
  | TARGET_USER | TEXT     | NOT NULL | 目标用户（与USERINFO中的USERNAME关联） |
  | SOURCE_USER | TEXT     | NOT NULL | 发送用户（与USERINFO中的USERNAME关联） |
  | TIME        | DATETIME | NOT NULL | 时间戳                                 |
  | CONTENT     | TEXT     | NOT NULL | 内容                                   |

  