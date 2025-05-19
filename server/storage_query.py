import asyncio
import websockets
import json
import asyncmy
import matplotlib.pyplot as plt
import numpy as np  # 添加numpy库
from io import BytesIO
import base64
from datetime import datetime

# 设置 matplotlib 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

async def storage_connection(websocket):
    try:
        async for message in websocket:
            try:
                # 接收前端发送的数据
                print(f"查询端收到数据: {message}")

                # 解析 JSON
                request = json.loads(message)
                action = request.get('action')
                print(f"查询判定值ACTION为{action}")

                if action == 'submitLevel':
                    # 获取用户名和视力数据
                    username = request.get('username')
                    print(f"获取用户名为{username}")
                    vision_data = request.get('level')
                    print(f"获取视力数据为{vision_data}")

                    # 连接到 MySQL 数据库
                    conn = await asyncmy.connect(
                        host='localhost',  # 数据库服务器地址
                        user='root',      # 数据库用户名
                        password='123456',  # 数据库密码
                        db='AIVISIONDATATEST'     # 数据库名
                    )

                    # 创建游标
                    cursor = conn.cursor()

                    # 获取当前时间，格式化为 YYYY-MM-DD
                    current_time = datetime.now().strftime('%Y-%m-%d')
                    await cursor.execute(
                        "INSERT INTO user_vision (username, data, timestamp) VALUES (%s, %s, %s)",
                        (username, vision_data, current_time)
                    )
                    await conn.commit()  # 提交事务

                    # 获取最近六次的历史记录
                    await cursor.execute(
                        "SELECT id, data, timestamp FROM user_vision WHERE username = %s ORDER BY id DESC LIMIT 6",
                        (username,)
                    )
                    records = await cursor.fetchall()

                    # 关闭游标和连接
                    await cursor.close()
                    conn.close()

                    if not records:
                        await websocket.send(json.dumps({'Back': '0'}))
                        print(f"用户{username}没有历史记录")
                        return

                    # 从记录中提取ID、数据值和时间戳
                    record_ids = [record[0] for record in records]
                    data_values = [float(record[1]) for record in records]
                    timestamps = [record[2] for record in records]

                    # 创建检查序号列表 (1, 2, 3, 4, 5, 6)，检查序号6对应最近的记录（最大的ID值）
                    check_numbers = list(range(1, len(records) + 1))[::-1]  # 反转列表，使检查序号6对应最大的ID值

                    # 创建ID到检查序号的映射
                    id_to_check_number = {}
                    for idx, record_id in enumerate(record_ids):
                        id_to_check_number[record_id] = check_numbers[idx]

                    # 创建折线图
                    plt.figure(figsize=(10, 6))
                    plt.plot(check_numbers, data_values, marker='o', linestyle='-', color='b')
                    plt.title(f'最近六次视力检查记录 - {username}')
                    plt.xlabel('检查序号')
                    plt.ylabel('视力值')
                    plt.grid(True)

                    # 设置横坐标刻度为检查序号
                    plt.xticks(check_numbers)

                    # 设置纵坐标间隔为0.1
                    min_val = min(data_values)
                    max_val = max(data_values)
                    y_ticks = np.arange(np.floor(min_val * 10) / 10, np.ceil(max_val * 10) / 10 + 0.1, 0.1)
                    plt.yticks(y_ticks)
                    plt.ylim(np.floor(min_val * 10) / 10 - 0.1, np.ceil(max_val * 10) / 10 + 0.1)

                    # 将图表转换为Base64编码的JPG图片
                    buffer = BytesIO()
                    plt.savefig(buffer, format='jpg')
                    buffer.seek(0)
                    image_data = base64.b64encode(buffer.read()).decode('utf-8')

                    # 发送图片数据和ID到检查序号的映射
                    await websocket.send(json.dumps({
                        'Back': '1',
                        'imgData': image_data
                    }))
                    print("发送历史数据图片成功")

                elif action == 'getHistory':
                    # 获取用户名
                    print("开始查询历史记录")
                    username = request.get('username')
                    print("历史记录获取其中用户名成功")

                    # 连接到 MySQL 数据库
                    conn = await asyncmy.connect(
                        host='localhost',
                        user='root',
                        password='123456',
                        db='AIVISIONDATATEST'
                    )

                    # 创建游标
                    cursor = conn.cursor()

                    # 获取最近六次的历史记录
                    await cursor.execute(
                        "SELECT id, data, timestamp FROM user_vision WHERE username = %s ORDER BY id DESC LIMIT 6",
                        (username,)
                    )
                    records = await cursor.fetchall()

                    # 关闭游标和连接
                    await cursor.close()
                    conn.close()

                    if not records:
                        # 用户不存在或没有历史记录
                        await websocket.send(json.dumps({'Back': '0'}))
                        print("用户不存在或没有历史记录")
                        return

                    # 从记录中提取ID、数据值和时间戳
                    record_ids = [record[0] for record in records]
                    data_values = [float(record[1]) for record in records]
                    timestamps = [record[2] for record in records]

                    # 创建检查序号列表 (1, 2, 3, 4, 5, 6)，检查序号6对应最近的记录（最大的ID值）
                    check_numbers = list(range(1, len(records) + 1))[::-1]  # 反转列表，使检查序号6对应最大的ID值

                    # 创建ID到检查序号的映射
                    id_to_check_number = {}
                    for idx, record_id in enumerate(record_ids):
                        id_to_check_number[record_id] = check_numbers[idx]

                    # 创建折线图
                    plt.figure(figsize=(10, 6))
                    plt.plot(check_numbers, data_values, marker='o', linestyle='-', color='b')
                    plt.title(f'用户{username}最近视力检查记录')
                    plt.xlabel('检查序号')
                    plt.ylabel('视力值')
                    plt.grid(True)

                    # 设置横坐标刻度为检查序号
                    plt.xticks(check_numbers)

                    # 设置纵坐标间隔为0.1
                    min_val = min(data_values)
                    max_val = max(data_values)
                    y_ticks = np.arange(np.floor(min_val * 10) / 10, np.ceil(max_val * 10) / 10 + 0.1, 0.1)
                    plt.yticks(y_ticks)
                    plt.ylim(np.floor(min_val * 10) / 10 - 0.1, np.ceil(max_val * 10) / 10 + 0.1)

                    # 将图表转换为Base64编码的JPG图片
                    buffer = BytesIO()
                    plt.savefig(buffer, format='jpg')
                    buffer.seek(0)
                    image_data = base64.b64encode(buffer.read()).decode('utf-8')

                    # 发送图片数据和ID到检查序号的映射
                    await websocket.send(json.dumps({
                        'Back': '1',
                        'imgData': image_data
                    }))
                    print("发送历史数据图片成功")

                else:
                    await websocket.send(json.dumps({'Back': False}))
            except Exception as e:
                print(f"处理错误：{e}")
    except websockets.ConnectionClosed as e:
        print(f"客户端关闭连接，代码: {e.code}，原因: {e.reason}")
    except Exception as e:
        print(f"处理错误: {e}")

async def main():
    # 启动 WebSocket 服务器
    async with websockets.serve(storage_connection, "localhost", 8770):
        print("服务器已启动，等待客户端连接...")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())