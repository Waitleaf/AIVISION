import asyncio
import websockets
import json
import asyncmy
# pip install cryptography 服务于asyncmy库

async def handle_connection(websocket):
    try:
        async for message in websocket:
            try:
                # 接收前端发送的数据
                # data = await websocket.recv()
                print(f"收到账户数据: {message}")

                # 解析 JSON
                request = json.loads(message)
                action = request.get('action')
                print(f"解析账户action为{action}")

                if action == 'login':
                    # 登录逻辑
                    credentials = request.get('credentials')
                    username = credentials['username']
                    password = credentials['password']

                    # 连接到 MySQL 数据库
                    conn = await asyncmy.connect(
                        host='localhost', #指数据库服务器地址，localhost为本地
                        user='root', #默认用户名
                        password='wait0612', #安装时设置的密码
                        db='AIVISION' #数据库名
                    )

                    # 创建游标
                    cursor = conn.cursor()

                    # 查询用户信息
                    await cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                    user = await cursor.fetchone()

                    # 关闭游标和连接
                    await cursor.close()
                    conn.close()

                    # 验证用户
                    if user:
                        response = json.dumps({"Back": True})
                    else:
                        response = json.dumps({"Back": False})

                elif action == 'register':
                    # 注册逻辑
                    credentials = request.get('credentials')
                    username = credentials['username']
                    password = credentials['password']
                    passwordKey = credentials['passwordKey']
                    passwordValue = credentials['passwordValue']

                    # 连接到 MySQL 数据库
                    conn = await asyncmy.connect(
                        host='localhost',
                        user='root',
                        password='wait0612',
                        db='AIVISION'
                    )

                    # 创建游标
                    cursor = conn.cursor()

                    # 检查用户名是否已存在
                    await cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    print(f"检查用户名{username}是否存在")
                    existing_user = await cursor.fetchone()

                    if existing_user:
                        response = json.dumps({"Back": False})
                    else:
                        # 插入新用户
                        await cursor.execute("INSERT INTO users (username, password, passwordKey, passwordValue) VALUES (%s, %s, %s, %s)", (username, password, passwordKey, passwordValue,))
                        await conn.commit()  # 提交新用户数据
                        response = json.dumps({"Back":True})

                    # 关闭游标和连接
                    await cursor.close()
                    conn.close()

                elif action == 'retrieve':
                    # 找回逻辑
                    credentials = request.get('credentials')
                    username = credentials['username']

                    # 连接到 MySQL 数据库
                    conn = await asyncmy.connect(
                        host='localhost',
                        user='root',
                        password='wait0612',
                        db='AIVISION'
                    )
                    
                    # 创建游标
                    async with conn.cursor() as cursor:
                        query="SELECT password, passwordKey, passwordValue FROM users WHERE username = %s"
                        await cursor.execute(query, (username,))
                        retrieve_user = await cursor.fetchone()

                    #验证并发送数据
                        if retrieve_user:
                            print(f"验证用户{username}成功，已发送用户信息")
                            password, passwordKey, passwordValue = retrieve_user
                            response = json.dumps({
                                "Back": True,
                                "password": password,
                                "passwordKey": passwordKey,
                                "passwordValue": passwordValue
                            })
                                            
                        else:
                            response = json.dumps({"Back":False})

                        # 关闭游标和连接
                        await cursor.close()
                        conn.close()

                else:
                    response = "无效的操作！"

                # 发送响应
                if response:
                    await websocket.send(response)

            except Exception as e:
                print(f"处理错误: {e}")       

    except websockets.ConnectionClosed as e:
        print(f"客户端关闭连接，代码: {e.code}，原因: {e.reason}")
    except Exception as e:
        print(f"处理错误: {e}")

async def main():
    # 启动 WebSocket 服务器
    async with websockets.serve(handle_connection, "localhost", 8769):
        print("服务器已启动，等待客户端连接...")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())