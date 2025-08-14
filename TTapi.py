import requests
import json
import threading
import socketio

login_url="http://localhost:25000/"
game_url="http://localhost:25001/"
room_url="http://localhost:25002/"
ADMIN_TOKEN = "admin_token" #管理员token

#房间信息处理
def room_info(room_data):
    room=room_data
    players=room_data.get('players')
    return room,players



#用户类
class User:
    def __init__(self, username=None, password=None): #用户初始化 参数为用户名和密码
        self.username = username
        self.password = password
        self.token = None #登录成功后会获得token服务器信任的唯一凭证
        self.uid = None #登录成功后会获得uid
        self.status = 0 #0表示未登录，1表示已登录
        self.room_data = None #创建或加入房间后会获得房间信息(该元素为json格式原始信息)
        self.room = {} #创建或加入房间后会获得房间信息(该元素为字典格式)
        self.room_players = [] #创建或加入房间后会获得房间玩家信息(该元素为列表格式)
        self.rooms=[] #获取所有房间信息后会获得所有房间信息(该元素为列表格式)
        self.sio=socketio.Client() #socketio初始化
        self.is_online=False #是否在线
        #socketio事件注册
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('join_room', self.on_join_room)
    
    def on_connect(self):  #socketio连接成功事件
        self.is_online=True
        print("socketio连接成功")

    def on_disconnect(self):  #socketio断开连接事件
        self.is_online=False
        print("socketio断开连接")

    def on_join_room(self, data):  #socketio加入房间事件
        if data.get('status') == 1001:
            print("加入房间失败，token无效")
            return
        elif data.get('status') == 1002:
            if data.get('message')=="Room_id is required":
                print("加入房间失败，房间号不能为空")
                return
            elif data.get('message')=="Room full":
                print("加入房间失败，房间已满")
                return
            elif data.get('message')=="Room not found":
                print("加入房间失败，房间不存在")
                return
            elif data.get('message')=="Player already in room":
                print("加入房间失败，玩家已在房间中")
                return
        elif data.get('status') == 1000:
            self.room_data = data['data']
            self.room,self.room_players = room_info(self.room_data)
            print("加入房间成功")
            print("房间号：",self.room_data['room_id'])
            return
        else:
            print("加入房间失败，未知错误")
            return


    

    def register(self):  #注册函数 返回值有五种：regis_success(注册成功), parameter_error(参数错误), username_exist(用户名已存在), network_error(网络错误), unknown_error(未知错误)
        upload_data = {'username': self.username, 'password': self.password}
        response = requests.post(login_url+"register", json=upload_data)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error"  #网络错误
        data=response.json()
        if data['status'] == 200:
            return "parameter_error" #参数错误
        elif data['status'] == 201:
            return "username_exist" #用户名已存在
        elif data['status'] == 202:
            self.token = data['token']
            self.uid = data['uid']
            self.status = 0
            return "regis_success" #注册成功
        else:
            return "unknown_error" #未知错误
        
    def connect(self):  #连接函数
        self.sio.connect(game_url, headers={'Authorization': self.token})

    def login(self):  #登录函数 返回值有五种：login_success(登录成功), parameter_error(参数错误), password_error(密码错误), network_error(网络错误), unknown_error(未知错误)
        upload_data = {'username': self.username, 'password': self.password}
        response = requests.post(login_url+"login", json=upload_data)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error" #网络错误
        data=response.json()
        if data['status'] == 100:
            return "parameter_error" #参数错误
        elif data['status'] == 101:
            return "password_error" #密码错误
        elif data['status'] == 102:
            self.token = data['token']
            self.uid = data['uid']
            self.status = 1
            try:
                self.sio.connect(game_url, auth={'token': self.token})
            except:
                print("连接失败")
            return "login_success" #登录成功
        else:
            return "unknown_error" #未知错误
        
    def create_room(self, playermax=6):  #创建房间函数 返回值有五种： not_login(未登录), create_success(创建成功), token_error(token无效), network_error(网络错误), unknown_error(未知错误)
        if self.status == 0:
            return "not_login" #未登录
        if self.token == None:
            return "not_login" #未登录
        upload_params = {'token': self.token}
        upload_data = {'playermax': playermax , 'uid': self.uid}
        response = requests.post(room_url+"create_room", params=upload_params, json=upload_data)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error" #网络错误
        data=response.json()
        if data['status'] == 1001:
            return "token_error" #token无效
        if data['status'] == 1002:
            if data['message']=="Room full! 房间已满":
                return "room_full" #房间已满
        if data['status'] == 1000:
            self.room_data = data['data']
            self.join_room_old(self.room_data['room_id'])
            return "create_success" #创建成功
        else:
            return "unknown_error" #未知错误
        
    def join_room_old(self, room_id):  #加入房间函数(以弃用) 返回值有五种： not_login(未登录), join_success(加入成功), token_error(token无效), room_not_exist(房间不存在或已满), network_error(网络错误), unknown_error(未知错误)
        if self.status == 0:
            return "not_login" #未登录
        if self.token == None:
            return "not_login" #未登录
        upload_params = {'token': self.token}
        upload_data = {'room_id': room_id, 'uid': self.uid}
        response = requests.post(room_url+"join_room", params=upload_params, json=upload_data)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error" #网络错误
        data=response.json()
        if data['status'] == 1001:
            return "token_error" #token无效
        if data['status'] == 1002:
            return "room_not_exist" #房间不存在或已满
        if data['status'] == 1000:
            self.room_data = data['data']
            self.room,self.room_players = room_info(self.room_data)
            return "join_success" #加入成功
        else:
            return "unknown_error" #未知错误
    
    def get_room_info(self, room_id=None):  #获取房间信息函数 返回值有五种： not_login(未登录), room_info(房间信息), token_error(token无效), room_not_exist(房间不存在或已满), network_error(网络错误), unknown_error(未知错误)
        if self.status == 0:
            return "not_login" #未登录
        if self.token == None:
            return "not_login" #未登录
        if self.room_data == None:
            return "room_not_exist" #房间不存在
        if room_id == None:
            room_id = self.room_data.get('room_id')
        if room_id == None:
            return "room_not_exist" #房间不存在
        upload_params = {'token': self.token, 'room_id': room_id}
        response = requests.get(room_url+"get_room_info", params=upload_params)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error" #网络错误
        data=response.json()
        if data['status'] == 1001:
            return "token_error" #token无效
        if data['status'] == 1002:
            return "room_not_exist" #房间不存在或已满
        if data['status'] == 1000:
            self.room_data=data.get('data')
            return self.room_data #房间信息
        else:
            return "unknown_error" #未知错误
    
    def get_all_room_info(self):  #获取所有房间信息函数 返回值有五种： not_login(未登录), all_rooms(所有房间信息), token_error(token无效), network_error(网络错误), unknown_error(未知错误)
        if self.status == 0:
            return "not_login" #未登录
        if self.token == None:
            return "not_login" #未登录
        upload_params = {'token': self.token}
        response = requests.get(room_url+"get_all_rooms", params=upload_params)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return "network_error" #网络错误
        data=response.json()
        if data['status'] == 1001:
            return "token_error" #token无效
        if data['status'] == 1000:
            temp_data=data.get('data')
            for i in temp_data:
                j={  
                    "room_id": i.get('room_id'),
                    "playermax": i.get('playermax'),
                    "player_num": i.get('player_num'),
                    "create_player": i.get('create_player'),
                }
                self.rooms.append(j)
            return self.rooms #所有房间信息
        else:
            return "unknown_error" #未知错误
    
    def join_room(self, room_id):  #加入房间函数 返回值有五种： not_login(未登录), join_success(加入成功), token_error(token无效), room_not_exist(房间不存在或已满), network_error(网络错误), unknown_error(未知错误)
        if self.status == 0:
            return "not_login" #未登录
        if self.token == None:
            return "not_login" #未登录
        emit_data = {'token': self.token, 'room_id': room_id, 'uid': self.uid}
        self.sio.emit('join_room', emit_data)
    
    
    
        

#管理员类(这里还处于新建文件夹状态)
class Admin: 
    def __init__(self, token=ADMIN_TOKEN): #管理员初始化 参数为token    
        self.token = token
        



        