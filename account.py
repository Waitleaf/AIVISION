import asyncio
import websockets
import json
import asyncmy

async def handle_connection(websocket):
    try:
        # 接收前端发送的数据
        data = await websocket.recv()
        print(f"收到数据: {data}")

        # 解析 JSON
        request = json.loads(data)
        action = request.get('action')

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
                response = "登录成功！"
            else:
                response = "账号或密码错误！"

        elif action == 'register':
            # 注册逻辑
            credentials = request.get('credentials')
            username = credentials['username']
            password = credentials['password']
            passwordKey=credentials['passwordKey']
            passwordValue=credentials['passwordValue']

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
            existing_user = await cursor.fetchone()

            if existing_user:
                response = "用户名已存在！"
            else:
                # 插入新用户
                await cursor.execute("INSERT INTO users (username, password, passwordKey, passwordValue) VALUES (%s, %s, %s, %s)", (username, password, passwordKey, passwordValue))
                await conn.commit()  # 提交事务

                response = "注册成功！"

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
            cursor = conn.cursor()

            # 检查用户名是否已存在，并查询四个值出来
            await cursor.execute("SELECT id, username, password, passwordKey, passwordValue FROM users WHERE username = %s", (username,))
            retrieve_user = await cursor.fetchone()

            # 关闭游标和连接
            await cursor.close()
            conn.close()

            #验证并发送数据
            if retrieve_user:
                password = user [1]
                passwordKey = user[2]
                passwordValue = user[3]
                response = json.dumps({
                    "password": password,
                    "passwordKey": passwordKey,
                    "passwordValue": passwordValue
                })
                                
            else:
                response = "您还未注册账号！"

        else:
            response = "无效的操作！"

        # 发送响应
        await websocket.send(response)
        
    except Exception as e:
        print(f"处理错误: {e}")

async def main():
    # 启动 WebSocket 服务器
    async with websockets.serve(handle_connection, "localhost", 8765):
        print("服务器已启动，等待客户端连接...")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())