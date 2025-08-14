import requests
from TTapi import *

# 云端服务器的 URL（根据你提供的 IP 和端口修改）
SERVER_URL = "http://106.55.54.216:25000"
#SERVER_URL = "http://localhost:25000"

# 测试注册功能
def test_register(username, password):
    url = f"{SERVER_URL}/register"
    data = {
        "username": username,
        "password": password
    }

    # 发送 POST 请求进行注册
    response = requests.post(url, json=data)
    response.encoding = "utf-8"
    data = response.json()

    if data.get("status")==202:
        print(f"注册成功: {response.json()}")
    elif data.get("status")==201 or data.get("status")==200:
        print(f"注册失败: {response.json()}")
    else:
        print(f"未知错误: {response.status_code} - {response.text}")

# 测试登录功能
def test_login(username, password):
    url = f"{SERVER_URL}/login"
    data = {
        "username": username,
        "password": password
    }

    # 发送 POST 请求进行登录
    response = requests.post(url, json=data)
    response.encoding = "utf-8"
    data = response.json()
    if data.get("status")==102:
        print(f"登录成功: {response.json()}")
    elif data.get("status")==101:
        print(f"登录失败: {response.json()}")
    else:
        print(f"未知错误: {response.status_code} - {response.text}")

# 你可以按需修改用户名和密码来测试
if __name__ == "__main__":
    '''# 测试注册
    test_register("testuser", "testpassword123")
    test_register("user123", "password123")

    # 测试登录
    test_login("testuser", "testpassword123")
    test_login("testuser", "wrongpassword")  # 错误密码测试
    test_login("user123", "password123")'''
    user=User()
    user.username="testuser"
    user.password="testpassword123"
    print(user.register())#注册
    print(user.login())#登录
    print(user.create_room())#创建房间
    print(user.join_room("1"))#加入房间



#["<token>":"<uid>","<token>":"<uid>","<token>":"<uid>","<token>":"<uid>"]


#################################################################################
'''user=User()
user.username="testuser"
user.password="testpassword123"
user.login()#登录
user.register()#注册
rooms_data=user.get_all_room_info()#获取所有房间信息

rooms_data=user.rooms
player_data=user.room_players'''






