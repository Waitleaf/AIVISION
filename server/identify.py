import asyncio
import cv2
import websockets
import base64
import mediapipe as mp
import random
import time
import numpy as np
import serial
import pyttsx3
import threading
from concurrent.futures import ThreadPoolExecutor

value = None
experience_img = 0
# hand_style = None  # 定义全局变量
shared_data = {"hand_style":None}
lock= asyncio.Lock()#锁对象
last_value = None  # 添加变量跟踪上一次的值
last_value_time = 0  # 添加时间戳记录上一次值变化的时间
value_stable_duration = 1.0  # 值需要保持稳定的时间(秒)

# 添加头部检测相关变量
mpdraw = None
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
drawSpec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)

def choose_random_value(arr):#定义一个函数，在一个列表中选取随机值
    # 使用 random 模块的 choice 函数选择一个随机元素
    random_value = random.choice(arr)
    return random_value

#********************检测函数**************
# 修改identity函数，添加防抖动机制
def identity(frame):
    global last_change_time, correct_count, width, current_size_index, wrong_count, level, window_width, window_height, value, hand_tip
    global last_value, last_value_time  # 添加新的全局变量
    
    # 获取帧的尺寸
    height, width = frame.shape[:2]
    
    # 计算动态位置 - 调整为更合适的位置
    text_x = int(width * 0.1)
    text_y = int(height * 0.6)
    
    # 计算字体大小 - 根据宽度动态调整，但设置最小值
    font_scale = max(1.5, width / 640 * 2.0)
    
    # 计算文本厚度 - 确保足够粗
    thickness = max(3, int(width / 640 * 4))
    
    # 添加文本背景以增强可读性
    text = ""
    color = (0, 255, 0)  # 默认绿色
    
    # 保存旧值用于比较
    old_value = value
    
    # 临时值，用于检测变化
    temp_value = None
    
    if hand_tip.x < arm.x - 0.05:
        text = L
        temp_value = 2
        color = (255, 0, 255)  # 紫色
    elif hand_tip.x > arm.x + 0.05:
        text = R
        temp_value = 3
        color = (0, 255, 255)  # 黄色
    elif hand_tip.y < arm.y - 0.05:
        text = U
        temp_value = 0
        color = (0, 255, 0)  # 绿色
    elif hand_tip.y > arm.y + 0.05:
        text = D
        temp_value = 1
        color = (0, 0, 255)  # 红色
    
    # 防抖动处理
    current_time = time.time()
    
    # 如果检测到的值与上次不同，更新时间戳
    if temp_value != last_value:
        last_value = temp_value
        last_value_time = current_time
        # 不立即更新value，等待稳定
    # 如果值保持稳定超过指定时间，才更新实际value
    elif temp_value is not None and (current_time - last_value_time) > value_stable_duration:
        if value != temp_value:  # 只有当value需要变化时才更新
            value = temp_value
            print(f"值稳定为: {value}")
    
    if text:
        # 获取文本大小
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # 确保文本框足够大
        padding_x = 30
        padding_y = 20
        
        # 绘制半透明背景 - 更大的背景框
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (text_x - padding_x, text_y - text_height - padding_y), 
                     (text_x + text_width + padding_x, text_y + padding_y), 
                     (0, 0, 0), 
                     -1)
        # 应用透明度
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # 绘制文本 - 先绘制黑色描边增强可读性
        cv2.putText(frame, text, (text_x-2, text_y-2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
        cv2.putText(frame, text, (text_x+2, text_y+2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
        # 绘制彩色文本
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
    
    # 添加防抖动状态指示器
    if temp_value is not None:
        stability_progress = min(1.0, (current_time - last_value_time) / value_stable_duration)
        bar_width = int(100 * stability_progress)
        cv2.rectangle(frame, (10, 10), (110, 20), (100, 100, 100), -1)
        cv2.rectangle(frame, (10, 10), (10 + bar_width, 20), (0, 255, 0), -1)

    return value
# 添加头部姿态检测函数
def detect_head_pose(frame):
    global value, last_value, last_value_time
    
    # 转换为RGB格式
    img_rgb = cv2.cvtColor(frame, code=cv2.COLOR_BGR2RGB)
    results = faceMesh.process(img_rgb)
    
    temp_value = None
    head_pose = None
    
    if results.multi_face_landmarks:
        for faceLms in results.multi_face_landmarks:
            # 绘制所有面部特征点
            mp.solutions.drawing_utils.draw_landmarks(frame, faceLms, mpFaceMesh.FACEMESH_CONTOURS,
                             drawSpec, drawSpec)
            
            # 获取关键点坐标用于判断头部方向
            h, w, c = frame.shape
            face_3d = []
            face_2d = []
            
            # 选择关键点（鼻尖、下巴、左眼、右眼、左嘴角、右嘴角）
            for idx, lm in enumerate(faceLms.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    x, y = int(lm.x * w), int(lm.y * h)
                    
                    # 2D坐标
                    face_2d.append([x, y])
                    
                    # 3D坐标
                    face_3d.append([x, y, lm.z])
            
            # 将列表转换为numpy数组
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)
            
            # 相机内参矩阵
            focal_length = 1 * w
            cam_matrix = np.array([[focal_length, 0, w / 2],
                                   [0, focal_length, h / 2],
                                   [0, 0, 1]])
            
            # 畸变系数
            dist_matrix = np.zeros((4, 1), dtype=np.float64)
            
            # 使用solvePnP解算姿态
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
            
            # 获取旋转矩阵
            rmat, jac = cv2.Rodrigues(rot_vec)
            
            # 获取角度
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            
            # 获取Y轴旋转角度（左右转动）
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360
            
            # 判断头部方向 - 修正上下方向判断并分离左右和上下的判断
            head_pose_vertical = ""
            head_pose_horizontal = ""
            
            # 水平方向判断（左右）
            if y < -10:
                head_pose_horizontal = "Left"
                temp_value = 2  # 左
            elif y > 10:
                head_pose_horizontal = "Right"
                temp_value = 3  # 右
            else:
                head_pose_horizontal = "Center"
            
            # 垂直方向判断（上下）- 修正方向
            if x > 10:  # 原来是 x < -10
                head_pose_vertical = "Up"
                temp_value = 0  # 上
            elif x < -10:  # 原来是 x > 10
                head_pose_vertical = "Down"
                temp_value = 1  # 下
            else:
                head_pose_vertical = "Level"
            
            # 最终方向
            if head_pose_horizontal != "Center":
                # 垂直不为center时，只显示左右方向
                head_pose = head_pose_horizontal
            elif head_pose_vertical != "Level":
                # 水平不为level，只显示上下方向
                head_pose = head_pose_vertical
            # 先左右再上下保证有上下时，可以覆盖到水平方向，显示上下方向
            elif head_pose_horizontal == "Center" and head_pose_vertical == "Level":
                # 水平、垂直都为center时，显示水平方向
                head_pose = "Center"
                temp_value = None  # 中心位置不触发动作
            else:
                # 其他情况，显示水平方向
                head_pose = head_pose_horizontal
            
            # 显示头部方向 - 分开显示垂直和水平方向
            # 创建背景
            overlay = frame.copy()
            # 使用矩形作为背景
            cv2.rectangle(overlay, (10, 20), (320, 220), (40, 40, 40), -1)
            alpha = 0.7  # 增加不透明度使文字更清晰
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            
            # 添加标题栏
            cv2.rectangle(frame, (10, 20), (320, 55), (70, 70, 70), -1)
            cv2.putText(frame, "Head Pose Detection", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # 状态指示器 
            status_color = (0, 255, 0)  # 默认绿色
            if head_pose != "Center":
                status_color = (0, 165, 255)  # 橙色，表示头部偏离中心
            cv2.circle(frame, (300, 38), 10, status_color, -1)
            
            # 主方向显示
            cv2.putText(frame, "Direction:", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, f"{head_pose}", (120, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 使用方向指示符
            if head_pose == "Left":
                cv2.putText(frame, "<-", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif head_pose == "Right":
                cv2.putText(frame, "->", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif head_pose == "Up":
                cv2.putText(frame, "^", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif head_pose == "Down":
                cv2.putText(frame, "v", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif head_pose == "Center":
                cv2.putText(frame, "o", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # 添加细节区域标题
            cv2.putText(frame, "Details:", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # 分开显示水平和垂直方向信息 
            cv2.putText(frame, "Horizontal:", (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
            cv2.putText(frame, f"{head_pose_horizontal}", (140, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
            
            cv2.putText(frame, "Vertical:", (40, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
            cv2.putText(frame, f"{head_pose_vertical}", (140, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 150, 100), 2)
            
            # 角度区域标题
            cv2.putText(frame, "Angles:", (20, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # 显示角度信息 
            cv2.putText(frame, f"X: {int(x)}", (90, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, f"Y: {int(y)}", (160, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 防抖动处理
            current_time = time.time()
            
            # 如果检测到的值与上次不同，更新时间戳和状态
            if temp_value != last_value:
                last_value = temp_value
                last_value_time = current_time
                value = None  # 确保在稳定前不发送值
            # 如果值保持稳定超过指定时间，才更新实际value
            elif (temp_value is not None and 
                temp_value == last_value and  # 确保值保持相同
                (current_time - last_value_time) > value_stable_duration):
                if value != temp_value:  # 只有当value需要变化时才更新
                    value = temp_value
                    print(f"头部姿态值稳定为: {value}")
                    last_value_time = current_time  # 重置时间戳，避免连续触发

            # 添加防抖动状态指示器
            if temp_value is not None:
                stability_progress = min(1.0, (current_time - last_value_time) / value_stable_duration)
                bar_width = int(100 * stability_progress)
                cv2.rectangle(frame, (10, 10), (110, 20), (100, 100, 100), -1)
                cv2.rectangle(frame, (10, 10), (10 + bar_width, 20), (0, 255, 0), -1)
    
    return frame


shared_data = {"hand_style":None}
lock= asyncio.Lock()#锁对象
#前端的按钮点击返回参数1/2
# global data
async def recive_data(websocket):
    global data
    data = await websocket.recv()
    print("接收参数：",data)
    # hand_style= data
    async with lock:
        shared_data["hand_style"]=data
    print("hand_style-r=",shared_data["hand_style"])

# 初始化语音引擎
# engines = [pyttsx3.init() for _ in range(4)]  # 创建4个语音引擎实例

# 创建四个线程池
# executor = ThreadPoolExecutor(max_workers=4)

# def speak(text):
#     """使用语音引擎朗读文本"""
#     # 选择一个语音引擎实例
#     engine = engines[experience_img]
#     engine.say(text)
#     engine.runAndWait()

# # 加载动图
# with open("./templates/picture-css/speak.gif", "rb") as image_file:
#     animated_gif = image_file.read()


#初始化人脸识别模块
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

experience_img=0
#初始化人脸识别模块
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# 初始化Holistic模型
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

#初始化一些变量
# value = None
R="Right"
L='Left'
U="Up"
D="Down"
a=b=c=d=e=f=g=h=i=j=k=l=m=n=x=y= 0
level=46

correct_count = 0
wrong_count = 0
count = [x,a,b,c,d,e,f,g,h,i,j,k,l,m,n,y]

# 初始化 Mediapipe Hands 模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
flag = ['Right','Left','Up','Down']


font = cv2.FONT_HERSHEY_SIMPLEX#这里定义了文字的字体类型

#现用time()函数获取现在的时间，赋值给变量last_change_time（上一次改变的时间）
last_change_time = time.time()
last_change_time_e = time.time()


# 修改websocket_handler函数，添加防重复发送机制
# 修改 websocket_handler 函数的防重复发送机制
async def websocket_handler(websocket):
    global value
    last_sent_value = None
    last_sent_time = 0
    min_send_interval = 2.0  # 最小发送间隔(秒)
    
    try:
        while True:
            current_time = time.time()
            
            # 增加更严格的发送条件判断
            if (value is not None and 
                value != last_sent_value and  # 确保值不同
                (current_time - last_sent_time) >= min_send_interval):  # 确保间隔足够
                
                print("send:", str(value))
                # 将值发送给 JavaScript 客户端
                await websocket.send(str(value))
                last_sent_value = value  # 更新上次发送的值
                last_sent_time = current_time  # 更新发送时间
                value = None  # 发送后立即清空，避免重复发送
            
            # 增加较短的休眠时间，避免过于频繁的检查
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error in websocket_handler: {e}")

# 修改 identity 函数中的防抖动机制
def identity(frame):
    global last_change_time, correct_count, width, current_size_index, wrong_count, level, window_width, window_height, value, hand_tip
    global last_value, last_value_time  # 添加新的全局变量
    
    # 获取帧的尺寸
    height, width = frame.shape[:2]
    
    # 计算动态位置 - 调整为更合适的位置
    text_x = int(width * 0.1)
    text_y = int(height * 0.6)
    
    # 计算字体大小 - 根据宽度动态调整，但设置最小值
    font_scale = max(1.5, width / 640 * 2.0)
    
    # 计算文本厚度 - 确保足够粗
    thickness = max(3, int(width / 640 * 4))
    
    # 添加文本背景以增强可读性
    text = ""
    color = (0, 255, 0)  # 默认绿色
    
    # 保存旧值用于比较
    old_value = value
    
    # 临时值，用于检测变化
    temp_value = None
    
    if hand_tip.x < arm.x - 0.05:
        text = L
        temp_value = 2
        color = (255, 0, 255)  # 紫色
    elif hand_tip.x > arm.x + 0.05:
        text = R
        temp_value = 3
        color = (0, 255, 255)  # 黄色
    elif hand_tip.y < arm.y - 0.05:
        text = U
        temp_value = 0
        color = (0, 255, 0)  # 绿色
    elif hand_tip.y > arm.y + 0.05:
        text = D
        temp_value = 1
        color = (0, 0, 255)  # 红色
    
    # 防抖动处理
    current_time = time.time()
    
    # 如果检测到的值与上次不同，更新时间戳和状态
    if temp_value != last_value:
        last_value = temp_value
        last_value_time = current_time
        value = None  # 确保在稳定前不发送值
    # 如果值保持稳定超过指定时间，才更新实际value
    elif (temp_value is not None and 
          temp_value == last_value and  # 确保值保持相同
          (current_time - last_value_time) > value_stable_duration):
        if value != temp_value:  # 只有当value需要变化时才更新
            value = temp_value
            print(f"值稳定为: {value}")
            last_value_time = current_time  # 重置时间戳，避免连续触发
    
    if text:
        # 获取文本大小
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # 确保文本框足够大
        padding_x = 30
        padding_y = 20
        
        # 绘制半透明背景 - 更大的背景框
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (text_x - padding_x, text_y - text_height - padding_y), 
                     (text_x + text_width + padding_x, text_y + padding_y), 
                     (0, 0, 0), 
                     -1)
        # 应用透明度
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # 绘制文本 - 先绘制黑色描边增强可读性
        cv2.putText(frame, text, (text_x-2, text_y-2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
        cv2.putText(frame, text, (text_x+2, text_y+2), font, font_scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
        # 绘制彩色文本
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
    
    # 添加防抖动状态指示器
    if temp_value is not None:
        stability_progress = min(1.0, (current_time - last_value_time) / value_stable_duration)
        bar_width = int(100 * stability_progress)
        cv2.rectangle(frame, (10, 10), (110, 20), (100, 100, 100), -1)
        cv2.rectangle(frame, (10, 10), (10 + bar_width, 20), (0, 255, 0), -1)

    return value

shared_data = {"hand_style":None}
lock= asyncio.Lock()#锁对象
#前端的按钮点击返回参数1/2
# global data
async def recive_data(websocket):
    global data
    data = await websocket.recv()
    print("接收参数：",data)
    # hand_style= data
    async with lock:
        shared_data["hand_style"]=data
    print("hand_style-r=",shared_data["hand_style"])

# 初始化语音引擎
# engines = [pyttsx3.init() for _ in range(4)]  # 创建4个语音引擎实例

# 创建四个线程池
# executor = ThreadPoolExecutor(max_workers=4)

# def speak(text):
#     """使用语音引擎朗读文本"""
#     # 选择一个语音引擎实例
#     engine = engines[experience_img]
#     engine.say(text)
#     engine.runAndWait()

# # 加载动图
# with open("./templates/picture-css/speak.gif", "rb") as image_file:
#     animated_gif = image_file.read()


#初始化人脸识别模块
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

experience_img=0
#初始化人脸识别模块
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# 初始化Holistic模型
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

#初始化一些变量
# value = None
R="Right"
L='Left'
U="Up"
D="Down"
a=b=c=d=e=f=g=h=i=j=k=l=m=n=x=y= 0
level=46

correct_count = 0
wrong_count = 0
count = [x,a,b,c,d,e,f,g,h,i,j,k,l,m,n,y]

# 初始化 Mediapipe Hands 模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
flag = ['Right','Left','Up','Down']


font = cv2.FONT_HERSHEY_SIMPLEX#这里定义了文字的字体类型

#现用time()函数获取现在的时间，赋值给变量last_change_time（上一次改变的时间）
last_change_time = time.time()
last_change_time_e = time.time()


# 修改视频流处理函数，在 hand_style == 5 时执行头部检测
async def video_stream(websocket):
    global last_change_time, random_img,flag,last_image,images_to_insert,resized_image,width,current_size_index,font,size,hands,mp_hands,count,correct_count,wrong_count,holistic,value,hand_tip,arm,R,D,L,U
    global experience_img,hand_tip,should_stop
    is_streaming = True  # 新增变量：表示当前是否正在传输视频流
    camera = cv2.VideoCapture(0)
    global data
    value = None
    R="Right"
    L='Left'
    U="Up"
    D="Down"

    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # 镜像画面，镜像后，左右相反
        frame = cv2.flip(frame, 1)
        async with lock:
            #不是空的时候才显示识别
            if shared_data["hand_style"] is not None:
                # 头部检测模式
                if int(shared_data["hand_style"]) == 5:
                    # 执行头部姿态检测
                    frame = detect_head_pose(frame)
                # 手势检测模式
                elif int(shared_data["hand_style"]) in [1, 2, 4]:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 获取人脸关键点和姿势信息（降低外界干扰）
                    results = hands.process(image)
                    results = holistic.process(image)

                    if results.pose_landmarks and results.face_landmarks and results.left_hand_landmarks and results.right_hand_landmarks:
                        # 在图像中绘制身体关键点和连接线
                        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

                    #手部节点
                    #右手（镜像后）
                    if (results.left_hand_landmarks and (int(shared_data["hand_style"])==2 or int(shared_data["hand_style"])==4)):
                        for landmark in results.left_hand_landmarks.landmark:
                            x = int(landmark.x * frame.shape[1])
                            y = int(landmark.y * frame.shape[0])
                            cv2.circle(frame, (x, y), 6, (255, 0, 255), -1)
                    #左手（镜像后）
                    if (results.right_hand_landmarks and int(shared_data["hand_style"]) == 1):
                        for landmark in results.right_hand_landmarks.landmark:
                            x = int(landmark.x * frame.shape[1])
                            y = int(landmark.y * frame.shape[0])
                            cv2.circle(frame, (x, y), 6, (255, 255, 0), -1)

                    if (int(shared_data["hand_style"]) == 1 and results.right_hand_landmarks):
                        # 获取第一只右手的关键点信息
                        right_hand_landmarks = results.right_hand_landmarks.landmark
                        # 获取整只手臂的坐标
                        arm = right_hand_landmarks[mp_hands.HandLandmark.WRIST]
                        hand_tip = right_hand_landmarks[mp_hands.HandLandmark.THUMB_TIP]
                        value = None
                        identity(frame)

                    elif (int(shared_data["hand_style"]) == 2 and results.left_hand_landmarks):
                        # 获取第一只左手的关键点信息
                        left_hand_landmarks = results.left_hand_landmarks.landmark
                        # 获取整只手臂的坐标
                        arm = left_hand_landmarks[mp_hands.HandLandmark.WRIST]
                        hand_tip = left_hand_landmarks[mp_hands.HandLandmark.THUMB_TIP]
                        value = None
                        identity(frame)

                    #*******示教
                    elif (int(shared_data["hand_style"]) == 4 and results.left_hand_landmarks):
                        left_hand_landmarks = results.left_hand_landmarks.landmark
                        # 获取整只手臂的坐标
                        arm = left_hand_landmarks[mp_hands.HandLandmark.WRIST]
                        hand_tip = left_hand_landmarks[mp_hands.HandLandmark.THUMB_TIP]
                        value = None
                        if experience_img == 0:
                            identity(frame)
                            if value==0:
                                experience_img+=1
                                print(experience_img)
                        elif experience_img == 1:
                            identity(frame)
                            if value==1:
                                experience_img+=1
                                print(experience_img)
                        elif experience_img == 2:
                            identity(frame)
                            if value==2:
                                experience_img+=1
                                print(experience_img)
                        elif experience_img == 3:
                            identity(frame)
                            if value ==3:
                                experience_img+=1
                                print(experience_img)
                        else:
                            identity(frame)
                
                # 关闭摄像头模式
                elif (int(shared_data["hand_style"]) == 3):
                    pass
                    # # 关闭摄像头
                    # camera.release()
                    # # 停止传输视频流
                    # is_streaming = False

        # 将帧转换为 Base64 编码的字符串
        _, buffer = cv2.imencode('.jpg', frame)
        frame_as_bytes = base64.b64encode(buffer)
        frame_as_text = frame_as_bytes.decode('utf-8')
        if is_streaming:
            # 发送帧到前端
            try:
                await websocket.send(frame_as_text)
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Connection closed unexpectedly: {e}")
                # 这里可以考虑关闭摄像头、清理资源等操作
                camera.release()
                is_streaming = False


async def serial_communication(websocket):
    global value
    while True:
        async with lock:
            if int(shared_data["hand_style"]) == 3:
                # 串口设置
                port = 'COM7'
                baudrate = 9600
                timeout = 1

                ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

                while True:
                    try:
                        received_data = ser.readline().strip()
                    except serial.SerialTimeoutException:
                        print("串行读取超时，跳过此次数据接收")
                    except Exception as e:
                        print(f"串行读取时遇到未知错误：{e}")
                    # print(received_data)
                    if received_data:
                        print("接收到语音数据")
                        if received_data == b'\x00':
                            value = "1"
                            break
                        elif received_data == b'\x01':
                            value = "0"
                            break
                        elif received_data == b'\x02':
                            value = "2"
                            break
                        elif received_data == b'\x03':
                            value = "3"
                            break

                        print("Received data:", value)  # 打印接收到的数据

                        print("speak-send:", str(value))

                    else:
                        print("Received nothings")

                ser.close()

                # 将值发送给 JavaScript 客户端
                await websocket.send(str(value))

                # 清除已发送的值，等待下一次通信
                value = None

            # 如果不是模式3，则休眠，避免频繁检查
            await asyncio.sleep(1)


# 启动 WebSocket 服务器
async def main():
    # 创建所有服务器
    servers = [
        websockets.serve(recive_data, "localhost", 8767),
        websockets.serve(websocket_handler, "localhost", 8765),
        websockets.serve(video_stream, "localhost", 8766),
        websockets.serve(serial_communication, "localhost", 8768)
    ]
    
    # 同时启动所有服务器
    await asyncio.gather(*servers)

if __name__ == "__main__":
    try:
        # 获取事件循环
        loop = asyncio.get_event_loop()
        # 运行主程序
        loop.run_until_complete(main())
        # 保持事件循环运行
        loop.run_forever()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        # 清理工作
        loop.close()
