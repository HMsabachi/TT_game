from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time
import threading
import os
import secrets
import bcrypt
from functools import wraps

login_listenServer = Flask("login_listenServer")
game_listenServer = Flask(__name__)
socketio = SocketIO(game_listenServer, cors_allowed_origins="*", async_mode='eventlet')
room_listenServer = Flask("room_listenServer")

# WebSocket认证装饰器
def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not request.sid:
            emit('error', {'message': 'Unauthorized'})
            return False
        return f(*args, **kwargs)
    return wrapped

# 定义全局变量
USER_DATABASE = [] # 用户数据库
UIDMAX = 1000000 # 最大UID
TOKEN_DATABASE = {} # 临时密钥数据库
ADMIN_TOKEN = 'VxyiBFWjotztsgFBkFPAJFj9-juMWTbNzj_y1I7cU1c' # 管理员token

#检查用户数据是否存在，不存在则创建
print(os.getcwd(),"为当前工作目录")
print(os.path.isfile('customer_data.json'),"是否存在customer_data.json")
if not os.path.isfile('customer_data.json'):
    print('Creating customer_data.json ... 创建用户数据文件...')
    json.dump({'USER_DATABASE': [], 'UIDMAX': 1000000}, open('customer_data.json', 'w'), indent=4)

customer_data = json.load(open('customer_data.json'))
print(customer_data)
# 定义用户数据库

USER_DATABASE = customer_data['USER_DATABASE'] # 用户数据库

UIDMAX = customer_data['UIDMAX'] # 最大UID

#自动保存用户数据
def save_data():
    global USER_DATABASE
    global UIDMAX
    print('Starting save_data thread... 启动自动保存用户数据线程...')
    print("当前设定的保存时间为300秒")
    time.sleep(20)
    while True:
        customer_data['USER_DATABASE'] = USER_DATABASE
        customer_data['UIDMAX'] = UIDMAX
        print('auto save data... 自动保存用户数据中...')
        json.dump(customer_data, open('customer_data.json', 'w'), indent=4)
        time.sleep(300)

#用户临时密钥
TOKEN_DATABASE = {}
#依据用户ID生成临时密钥
def generate_token(uid):
    token = secrets.token_urlsafe(32)
    TOKEN_DATABASE[token] = uid
    return token

#验证临时密钥是否有效
def verify_token(token):
    if token is None:
        return None
    if token in TOKEN_DATABASE:
        return TOKEN_DATABASE[token]
    else:
        return None
    
#密码加密算法
def hash_password(plain_password: str):
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#密码验证算法
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#通过uid获取用户信息
def get_user_info(uid):
    for user in USER_DATABASE:
        if user['uid'] == uid:
            return user
    return None





# 登录接口
@login_listenServer.route('/login', methods=['POST','GET'])
def login():

    global UIDMAX
    global USER_DATABASE
    # 获取请求体中的 JSON 数据
    data = request.json
    if not data:
        return jsonify({"message": "Invalid request! 无效的请求","status":100}), 200

    # 检查请求体中是否有必要的数据
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required! 服务器没有收到用户名或密码","status":100}), 200

    # 获取用户名和密码
    username = data.get('username')
    password = data.get('password')

    # 验证用户名和密码是否正确
    for user in USER_DATABASE:
        if user['username'] == username and verify_password(password, user['password']):
            # 生成临时密钥
            token = generate_token(user['uid'])
            # 返回 token 和 uid
            return jsonify({"message": "Login successful! 登录成功", "status": 102, "token": token, "uid": user['uid']}), 200

    # 用户名或密码错误
    else:
        return jsonify({"message": "Invalid username or password! 用户名或密码错误","status":101}), 200

# 注册接口
@login_listenServer.route('/register', methods=['POST','GET'])
def register():
    data = request.json
    if not data:
        return jsonify({"message": "Invalid request! 无效的请求","status":200}), 200
    global UIDMAX
    global USER_DATABASE
    # 检查请求体中的数据
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required! 服务器没有收到用户名或密码","status":200}), 200

    username = data['username']
    password = data['password']

    for user in USER_DATABASE:
        if user['username'] == username:
            return jsonify({"message": "Username already exists! 用户名已存在","status":201}), 200

    # 密码加密
    hashed_password = hash_password(password)
    # 保存用户信息（用户名和加密后的密码）
    print(type(UIDMAX))
    print("当前最大UID为%d",UIDMAX)
    UIDMAX += 1 # 自增UID
    USER_DATABASE.append({'username': username, 'password': hashed_password, 'uid': UIDMAX})
    #创建临时密钥
    token = generate_token(UIDMAX)
    #返回token
    return jsonify({"message": "Registration successful! 注册成功","status":202,"token":token,"uid":UIDMAX}), 200

#管理员测试接口
#获取用户数据库和token数据库
@login_listenServer.route('/admin_get_data', methods=['GET'])
def admin_get_data():
    token=request.args.get('token')
    if token==ADMIN_TOKEN:
        #返回用户数据库和token数据库
        return jsonify({
            "USER_DATABASE": USER_DATABASE,
            "TOKEN_DATABASE": TOKEN_DATABASE,
            "message": "Admin page! 管理员页面",
            "status": 300
        }), 200
    else:
        return jsonify({"message": "Invalid token! 无效的token","status":301}),200
#发送用户数据
@login_listenServer.route('/admin_send_data', methods=['POST','GET'])
def admin_send_data():
    token=request.args.get('token')
    if token==ADMIN_TOKEN:
        #接收用户数据
        data = request.json
        if not data:
            return jsonify({"message": "Invalid request! 无效的请求","status":302}), 200
        global USER_DATABASE
        global UIDMAX
        global TOKEN_DATABASE
        USER_DATABASE=data['USER_DATABASE']
        UIDMAX=data['UIDMAX']
        TOKEN_DATABASE=data['TOKEN_DATABASE']
        return jsonify({"message": "Data received! 数据已接收","status":300}), 200
    else:
        return jsonify({"message": "Invalid token! 无效的token","status":301}), 200

#获取token接口
@login_listenServer.route('/get_token', methods=['GET'])
def get_token():
    global TOKEN_DATABASE
    # 获取请求参数中的 token
    token = request.args.get('token')
    # 验证 token 是否有效
    if token == ADMIN_TOKEN:
        return jsonify(
            {
                "message": "Token is valid! 有效的token",
                "status": 1000,
                "TOKEN_DATABASE": TOKEN_DATABASE
            }
        ), 200
    else:
        return jsonify({"message": "Invalid token! 无效的token","status":1001}), 200
    

###################################### 游戏服务器 ##############

# 游戏服务器
GAMEROOMS = {
    'room_num_max': 10, # 最大房间数量
    'room_list': [] # 房间列表
} # 游戏房间

class Room:
    def __init__(self, room_id, playermax,create_player): # 房间号，最大人数     room_full/ok(房间数量已达上限/创建房间成功)
        self.room_id = room_id # 房间号
        self.playermax = playermax # 房间最大人数
        self.start_time = time.time() # 房间开始时间
        self.status = 'waiting' # 房间状态 waiting/playing/finished
        self.create_player=create_player # 创建房间的玩家对象
        self.score_list = [] # 玩家得分列表
        self.players=[] # 玩家列表
        self.is_start=False # 是否开始游戏
        self.is_end=False # 是否结束游戏
        self.port=0 # 房间端口号
        self.host='' # 房间主机地址
        self.players_ready=0 # 玩家准备数量
        self.players_live=0 # 玩家存活数量
        print('创建房间成功 room_id={room_id}, playermax={playermax}')
    

    def player_num(self): #当前房间人数
        return len(self.players)
    
    def player_list(self): #当前房间玩家列表
        return self.players
    
    def info(self): #房间信息
        players_info=[]
        for player in self.players:
            players_info.append(player.info())
        return {
            'room_id': self.room_id,
            'playermax': self.playermax,
            'player_num': self.player_num(),
            'create_player': self.create_player,
            'players': players_info,
            'start_time': self.start_time,
            'status': self.status,
            'score_list': self.score_list,
            'port': self.port,
            'host': self.host,
            'players_ready': self.players_ready,
            'players_live': self.players_live
        }

    def add_player(self, uid): #添加玩家 unfound/full/already/ok(未找到uid/房间已满/玩家已在房间中/添加成功) 
        print('尝试添加玩家 uid=%d', uid)
        global USER_DATABASE
        for users in USER_DATABASE:
            if users['uid'] == uid:
                user=users
                break
        else:
            print('未找到uid')
            return "unfound"
        if self.player_num() >= self.playermax:
            print('房间已满')
            return "full"
        if self.is_player_in_room(uid):
            print('玩家已在房间中')
            return "already"
        #创建玩家对象
        pid = len(self.players) + 1
        player = Player(user, pid)
        self.players.append(player)
        print('添加玩家成功 uid=%d', uid)
        return 'ok'

    def remove_player(self, uid): #移除玩家 unfound/not_in_room/ok(未找到uid/玩家不在房间中/移除成功)
        print('尝试移除玩家 uid=%d', uid)
        global USER_DATABASE
        for users in USER_DATABASE:
            if users['uid'] == uid:
                user=users
                break
        else:
            print('未找到uid')
            return "unfound"
        for player in self.players:
            if  player.uid == user['uid']:
                self.players.remove(player)
                print('移除玩家成功 uid=%d', uid)
                return 'ok'
        else:
            print('玩家不在房间中')
            return 'not_in_room'
    #通过uid判断玩家是否在房间中
    def is_player_in_room(self,uid):
        for player in self.players:
            if player.uid == uid:
                return True
        else:
            return False
    #通过uid获取玩家对象
    def get_player_by_uid(self,uid):
        for player in self.players:
            if player.uid == uid:
                return player
        else:
            return None
      
#玩家类
class Player:
    def __init__(self,user,id):
        self.uid=user['uid']
        self.id=id
        self.name=user['username']
        self.pos=(0,0)
        self.angle=0
        self.hp=100
        self.bullets=[]
        self.weapons=[]
        self.is_live=True
        self.is_ready=False
        self.col1=('','','')
        self.col2=('','','')
        self.col3=('','','')
        self.is_winner=False
    def info(self):
        return {
            'uid': self.uid,
            'id': self.id,
            'name': self.name,
            'pos': self.pos,
            'angle': self.angle,
            'hp': self.hp,
            'bullets': self.bullets,
            'weapons': self.weapons,
            'is_live': self.is_live,
            'is_ready': self.is_ready,
            'col1': self.col1,
            'col2': self.col2,
            'col3': self.col3,
            'is_winner': self.is_winner
        }

#游戏房间接口
@room_listenServer.route('/create_room', methods=['POST','GET'])
def create_room():
    print('接收到尝试创建房间请求')
    try:
        data = request.json
    except:
        print('无效的请求')
        return jsonify({"message": "Invalid request! 无效的请求","status":1002,"data":{}}), 200
    #检查token是否有效
    token = request.args.get('token')
    uid = verify_token(token)
    if not token or uid is None:
        print('无效的token')
        return jsonify({"message": "Invalid token! 无效的token","status":1001,"data":{}}), 200
    global GAMEROOMS
    # 检查请求体中的数据
    if not data or not data.get('playermax'):
        print('参数playermax缺失')
        return jsonify({"message": "Playermax is required! 服务器没有收到playermax","status":1002,"data":{}}), 200
    playermax = data['playermax']
    # 创建房间
    # 判断房间数量是否达到上限
    if GAMEROOMS['room_num_max'] != 0 and len(GAMEROOMS['room_list']) >= GAMEROOMS['room_num_max']:
        print('房间数量已达上限')
        return jsonify({"message": "Room full! 房间已满","status":1002}), 200
    create_player=get_user_info(uid)
    room_id = len(GAMEROOMS['room_list']) + 1 ### 1 2 3 4 5 6  8 9 10 10
    room = Room(room_id, playermax,create_player)
    GAMEROOMS['room_list'].append(room)
    print('创建房间成功 room_id=%d, playermax=%d', room_id, playermax)
    data=room.info()
    return jsonify({"message": "Create room successful! 创建房间成功","status":1000,'data':data}), 200


    
#获取单个房间信息接口
@room_listenServer.route('/get_room_info', methods=['GET'])
def get_room_info():
    print('接收到获取房间信息请求')
    #检查token是否有效
    token = request.args.get('token')
    uid = verify_token(token)
    if not token or uid is None:
        print('无效的token')
        return jsonify({"message": "Invalid token! 无效的token","status":1001,"data":{}}), 200
    global GAMEROOMS
    # 检查请求体中的数据
    try:
        room_id = int(request.args.get('room_id'))
    except Exception:
        print('参数room_id缺失')
        return jsonify({"message": "Room_id is required! 服务器没有收到room_id","status":1002,"data":{}}), 200
    if not request.args.get('room_id'):
        print('参数room_id缺失')
        return jsonify({"message": "Room_id is required! 服务器没有收到room_id","status":1002,"data":{}}), 200
    
    # 获取房间信息
    for room in GAMEROOMS['room_list']:
        if room.room_id == room_id:
            data=room.info()
            return jsonify({"message": "Get room info successful! 获取房间信息成功","status":1000,'data':data}), 200
    else:
        print('未找到房间')
        return jsonify({"message": "Room not found! 未找到房间","status":1002}), 200

#获取全部房间信息接口
@room_listenServer.route('/get_all_room_info', methods=['GET'])
def get_all_room_info():
    print('接收到获取全部房间信息请求')
    #检查token是否有效
    token = request.args.get('token')
    uid = verify_token(token)
    if not token or uid is None:
        print('无效的token')
        return jsonify({"message": "Invalid token! 无效的token","status":1001,"data":{}}), 200
    global GAMEROOMS
    # 获取房间信息
    data=[]
    for room in GAMEROOMS['room_list']:
        data.append(room.info())
    print('获取全部房间信息成功')
    return jsonify({"message": "Get all room info successful! 获取全部房间信息成功","status":1000,'data':data}), 200

#游戏准备接口 (废弃)
@room_listenServer.route('/game_ready', methods=['POST','GET'])
def game_ready():
    print('接收到游戏准备请求')
    data = request.json
    if not data:
        print('无效的请求')
        return jsonify({"message": "Invalid request! 无效的请求","status":1002,"data":{}}), 200
    #检查token是否有效
    token = request.args.get('token')
    uid = verify_token(token)
    if not token or uid is None:
        print('无效的token')
        return jsonify({"message": "Invalid token! 无效的token","status":1001,"data":{}}), 200
    global GAMEROOMS
    # 检查请求体中的数据
    if not data or not data.get('room_id') or not data.get('uid'):
        print('参数room_id或uid缺失')
        return jsonify({"message": "Room_id and uid are required! 服务器没有收到room_id或uid","status":1002,"data":{}}), 200
    if uid != data['uid']:
        print('uid不匹配')
        return jsonify({"message": "Uid not match! uid不匹配","status":1002,"data":{}}), 200
    # 获取房间号
    room_id = int(data['room_id'])
    # 加入房间
    for room in GAMEROOMS['room_list']:
        if room.room_id == room_id:
            player=room.get_player_by_uid(uid)
            if player is None:
                print('未找到玩家')
                return jsonify({"message": "Player not found! 未找到玩家","status":1002,"data":{}}), 200
            if player.is_ready:
                print('玩家已经准备')
                return jsonify({"message": "Player is already ready! 玩家已经准备","status":1002,"data":{}}), 200
            player.is_ready=True
            print('玩家准备成功')
            return jsonify({"message": "Player ready successful! 玩家准备成功","status":1000, "data":{"host":room.host,"port":room.port}}), 200
    else:
        print('未找到房间')
        return jsonify({"message": "Room not found! 未找到房间","status":1002,"data":{}}), 200

'''
#以下内容废弃============================================================

#多线程登录接口
def login_thread():
    login_listenServer.run(debug=False, host='0.0.0.0', port=25000)
#多线程游戏接口
#def game_thread():
    #game_listenServer.run(debug=False, host='0.0.0.0', port=25001)
#多线程房间接口
def room_thread():
    room_listenServer.run(debug=False, host='0.0.0.0', port=25002)

# 以上内容废弃===========================================================
'''

# WebSocket事件处理
name_space = '/game'

@socketio.on('connect') # 客户端连接
def handle_connect(auth):
    print(f'客户端尝试连接: {request.sid}\n 传入auth={auth}\n 客户端IP: {request.remote_addr}')
    if not auth:
        print('无效的auth, 断开连接')
        return False
    # 验证token
    if not auth.get('token'):
        print('无效的token, 断开连接')
        return False
    uid=verify_token(auth['token'])
    if not uid:
        print('无效的token, 断开连接')
        return False
    emit('auth_success', {'message':'Auth success','status':1000,'data':{'uid':uid}}, to=request.sid)

@socketio.on('disconnect') # 客户端断开连接
def handle_disconnect():
    print(f'客户端断开连接: {request.sid}')
    

@socketio.on('join_room') # 加入房间
@authenticated_only
def handle_join_room(data):
    event_name = "join_room"
    try:
        print(f'客户端加入房间: {request.sid} {data}')
        room_id = int(data['room_id'])
        token = data['token']
        uid = verify_token(token)
        if not uid:
            emit(event_name, {'message': 'Invalid token','status': 1001, 'data': {}}, to = request.sid)
            return
        if not room_id:
            emit(event_name, {'message': 'Room_id is required','status': 1002, 'data': {}}, to = request.sid)
            return
        global GAMEROOMS
        for room in GAMEROOMS['room_list']:
            if room.room_id == room_id:
                result=room.add_player(uid)
                if result=='ok':
                    data=room.info()
                    join_room(str(room_id))
                    emit(event_name, {
                        'message':"Join room successful",
                        'status':1000,
                         'data':data
                    }, to = request.sid)
                    # 通知房间内其他玩家
                    emit('room_update', {
                        'message':'Player join room',
                        'type':'join', 
                        'user_id':uid,
                        'room_id':room_id,
                        'status':1000,
                        'data':data
                    } ,room = str(room_id))
                    return
                elif result=='full':
                    emit(event_name, {'message': 'Room full','status': 1002, 'data': {}}, to = request.sid)
                    return
                elif result=='already':
                    emit(event_name, {'message': 'Player already in room','status': 1002, 'data': {}}, to = request.sid)
                    return
                else:
                    emit(event_name, {'message': 'Player not found','status': 1002, 'data': {}}, to = request.sid)
                    return
        else:
            emit(event_name, {'message': 'Room not found','status': 1002, 'data': {}}, to = request.sid)
            return
        
    except Exception as e:
        emit(event_name, {'message': str(e)}, to = request.sid)

@socketio.on('leave_room')
@authenticated_only
def handle_leave_room(data):
    try:
        room_id = str(data['room_id'])
        token = data['token']
        uid = verify_token(token)
        event_name = "leave_room"
        if not uid:
            emit(event_name, {'message': 'Invalid token','status': 1001, 'data': {}}, to = request.sid)
            return
        
        leave_room(room_id)
        emit('room_update', {
            'type': 'leave', 
            'user_id': uid,
            'room_id': room_id
        }, room=room_id)
        
    except Exception as e:
        emit('error', {'message': str(e)})

# 启动服务器
if __name__ == '__main__':
     # 启动自动保存用户数据线程
    t = threading.Thread(target=save_data , args=(), daemon=True)
    t.start()
    # 启动HTTP服务
    threading.Thread(target=login_listenServer.run, kwargs={'host':'0.0.0.0','port':25000, 'use_reloader':False}, daemon=True).start()
    threading.Thread(target=room_listenServer.run, kwargs={'host':'0.0.0.0','port':25002, 'use_reloader':False}, daemon=True).start()
    # 启动WebSocket服务
    socketio.run(game_listenServer, host='0.0.0.0', port=25001, debug=False ,use_reloader=False)
   

'''
status code类型说明
100 登陆时缺少必要参数
101 登陆时用户名或密码错误
102 登陆成功
200 注册时缺少必要参数
201 用户名已存在
202 注册成功
300 管理员页面 获取用户数据库和token数据库 发送用户数据
301 管理员页面 无效的token
1000 游戏过程中数据正常获取
1001 游戏过程中token失效
1002 游戏过程中数据异常
'''
'''
管理员token: VxyiBFWjotztsgFBkFPAJFj9-juMWTbNzj_y1I7cU1c
测试用户token: CXKkdu5h95ewJ0tTTAqsw_O6sKS5t1FOjKqnXQcyrIU
'''




#加入房间接口(废弃)
@room_listenServer.route('/join_room_old', methods=['POST','GET']) #已废弃
def join_room_old():
    print('接收到尝试加入房间请求')
    data = request.json
    if not data:
        print('无效的请求')
        return jsonify({"message": "Invalid request! 无效的请求","status":1002,"data":{}}), 200
    #检查token是否有效
    token = request.args.get('token')
    uid = verify_token(token)
    if not token or uid is None:
        print('无效的token')
        return jsonify({"message": "Invalid token! 无效的token","status":1001,"data":{}}), 200
    global GAMEROOMS
    # 检查请求体中的数据
    if not data or not data.get('room_id') or not data.get('uid'):
        print('参数room_id或uid缺失')
        return jsonify({"message": "Room_id and uid are required! 服务器没有收到room_id或uid","status":1002,"data":{}}), 200
    if uid != data['uid']:
        print('uid不匹配')
        return jsonify({"message": "Uid not match! uid不匹配","status":1002,"data":{}}), 200
    # 获取房间号
    room_id = int(data['room_id'])
    # 加入房间
    for room in GAMEROOMS['room_list']:
        if room.room_id == room_id:
            result=room.add_player(uid)
            if result=='ok':
                data=room.info()
                return jsonify({"message": "Join room successful! 加入房间成功","status":1000,'data':data}), 200
            elif result=='full':
                print('房间已满')
                return jsonify({"message": "Room full! 房间已满","status":1002}), 200
            elif result=='already':
                print('玩家已在房间中')
                return jsonify({"message": "Player already in room! 玩家已在房间中","status":1002}), 200
            else:
                print('未找到uid')
                return jsonify({"message": "Player not found! 未找到uid","status":1002}), 200
    else:
        print('未找到房间')
        return jsonify({"message": "Room not found! 未找到房间","status":1002}), 200