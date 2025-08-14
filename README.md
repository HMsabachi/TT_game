
# 服务端 API 文档

## 1. 基本信息
- **基础 URL**: `http://106.55.54.216:25000`
- **数据格式**: 所有请求和响应均为 JSON
- **身份验证**:
  - 注册和登录不需要 token
  - 登录成功后返回的 `token` 用于后续验证

---

## 2. 接口列表

### 注册接口
- **URL**: `/register`
- **方法**: `POST`
- **请求参数**（JSON）:
```json
{
    "username": "string",   // 用户名
    "password": "string"    // 密码（明文）
}
```
- **返回示例**:
```json
{
    "message": "Registration successful! 注册成功",
    "status": 202,
    "token": "用户临时密钥",
    "uid": 1000001
}
```
- **状态码说明**:
  - 200：缺少必要参数
  - 201：用户名已存在
  - 202：注册成功

---

### 登录接口
- **URL**: `/login`
- **方法**: `POST`
- **请求参数**（JSON）:
```json
{
    "username": "string",  // 用户名
    "password": "string"   // 密码（明文）
}
```
- **返回示例**:
```json
{
    "message": "Login successful! 登录成功",
    "status": 102,
    "token": "用户临时密钥",
    "uid": 1000001
}
```
- **状态码说明**:
  - 100：缺少必要参数
  - 101：用户名或密码错误
  - 102：登录成功

---

### 管理员获取数据接口
- **URL**: `/admin_get_data`
- **方法**: `GET`
- **参数**（Query）:
```
token=管理员密钥
```
- **返回示例**:
```json
{
    "USER_DATABASE": [...],
    "TOKEN_DATABASE": {...},
    "message": "Admin page! 管理员页面",
    "status": 300
}
```
- **状态码说明**:
  - 300：获取成功
  - 301：无效 token

---

### 管理员更新数据接口
- **URL**: `/admin_send_data`
- **方法**: `POST`
- **参数**（Query）:
```
token=管理员密钥
```
- **请求 JSON**:
```json
{
    "USER_DATABASE": [...],
    "UIDMAX": 1000005
}
```
- **返回示例**:
```json
{
    "message": "Data received! 数据已接收",
    "status": 300
}
```

---
### 管理员获取Token接口
- **URL**: `/get_token`
- **方法**: `GET`   
- **参数**（Query）:
```
token=管理员密钥
```

- **返回示例**:
```json
{
    "message": "Token is valid! 有效的token",
    "status": 1000,
    "USER_DATABASE": "{...}"
 }
```
- **状态码说明**:
  - 1000：获取成功
  - 1001：无效 token

---
### 创建游戏房间接口
- **URL**: `/create_room`
- **方法**: `POST`
- **参数**: `Query`:
```
   token=用户临时密钥
```
- **请求参数**（JSON）:
```json
{
    "playermax": 6,    // 房间最大人数
}
```
- **返回示例**:
```json
{
    "data": {       // 房间信息
        "player_num": 0,   // 房间当前人数
        "playermax": 6,    // 房间最大人数
        "players": [],     // 房间当前玩家列表
        "room_id": 1,      // 房间ID
        "score_list": [],  // 房间得分列表
        "start_time": 1755001878.168409,  // 房间开始时间
        "status": "waiting"  // 房间状态  (waiting/playing/finished)
    },
    "message": "Create room successful! 创建房间成功",
    "status": 1000
}
```
- **状态码说明**:
  - 1000：创建成功
  - 1001：无效 token
  - 1002：参数错误/房间已到达能创建的最大数
---
### 加入游戏房间接口
- **URL**: `/join_room`   
- **方法**: `POST`
- **参数**: `Query`:
```
   token=用户临时密钥
```
- **请求参数**（JSON）:
```json
{
    "room_id":1,  // 房间ID
    "uid":1000003  // 用户ID
}
```
- **返回示例**:
```json
{
    "data": {
        "player_num": 1,
        "playermax": 6,
        "players": [
            {
                "angle": 0,
                "bullets": [],
                "col1": ["","",""],
                "col2": ["","",""],
                "col3": ["","",""],
                "hp": 100,
                "id": 1,
                "is_live": true,
                "is_ready": false,
                "is_winner": false,
                "name": "lsdhuwda",
                "pos": [0,0],
                "uid": 1000003,
                "weapons": []
            }
        ],
        "room_id": 1,
        "score_list": [],
        "start_time": 1755001878.168409,
        "status": "waiting"
    },
    "message": "Join room successful! 加入房间成功",
    "status": 1000
}
```
- **状态码说明**:
  - 1000：加入成功成功
  - 1001：无效 token
  - 1002：参数错误/房间不存在/房间已满
---
### 获取单个房间信息接口
- **URL**: `/get_room_info `   
- **方法**: `GET`
- **参数**: `Query`:
```
    token=用户临时密钥
    room_id=房间ID
```
- **返回示例**:
```json
{
    "data": {
        "player_num": 1,
        "playermax": 6,
        "players": [
            {
                "angle": 0,
                "bullets": [],
                "col1": ["","",""],
                "col2": ["","",""],
                "col3": ["","",""],
                "hp": 100,
                "id": 1,
                "is_live": true,
                "is_ready": false,
                "is_winner": false,
                "name": "lsdhuwda",
                "pos": [0,0],
                "uid": 1000003,
                "weapons": []
            }
        ],
        "room_id": 1,
        "score_list": [],
        "start_time": 1755001878.168409,
        "status": "waiting"
    },
    "message": "Get room info successful! 获取房间信息成功",
    "status": 1000
}
```
- **状态码说明**:
  - 1000：获取成功
  - 1001：无效 token
  - 1002：参数错误/房间不存在
---
### 获取所有房间信息接口
- **URL**: `/get_all_room_info `   
- **方法**: `GET`
- **参数**: `Query`:
```
    token=用户临时密钥
```
- **返回示例**:
```json
{
    "data": [
        {
            "player_num": 1,
            "playermax": 6,
            "players": 
            [{
                "angle": 0,
                "bullets": [],
                "col1": ["","",""],
                "col2": ["","",""],
                "col3": ["","",""],
                "hp": 100,
                "id": 1,
                "is_live": true,
                "is_ready": false,
                "is_winner": false,
                "name": "lsdhuwda",
                "pos": [0,0],
                "uid": 1000003,
                "weapons": []
            }],
            "room_id": 1,
            "score_list": [],
            "start_time": 1755001878.168409,
            "status": "waiting"
        }
    ],
    "message": "Get all room info successful! 获取全部房间信息成功",
    "status": 1000
}
```
- **状态码说明**:
  - 1000：获取成功
  - 1001：无效 token
  - 1002：参数错误/房间不存在
---
## 3.状态码说明
  - 100 登陆时缺少必要参数
  - 101 登陆时用户名或密码错误
  - 102 登陆成功
  - 200 注册时缺少必要参数
  - 201 用户名已存在
  - 202 注册成功
  - 300 管理员页面 获取用户数据库和token数据库 发送用户数据
  - 301 管理员页面 无效的token
  - 1000 游戏过程中数据正常获取
  - 1001 游戏过程中token失效
  - 1002 游戏过程中数据异常
---
## 4. 注意事项
1. 所有密码在传输前应通过 HTTP 进行传输。
2. token 仅在一定时间内有效。
3. 管理员接口应确保密钥安全，不要暴露给普通用户。
