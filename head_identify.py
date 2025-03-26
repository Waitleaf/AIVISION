import cv2
import mediapipe as mp
import numpy as np

mpdraw = None
Pre_time = None

def face_detect():
    global mpdraw, Pre_time
    cap = cv2.VideoCapture(0)

    # 使用Face Mesh代替Face Detection以获取更多面部特征点
    mpFaceMesh = mp.solutions.face_mesh
    mpdraw = mp.solutions.drawing_utils
    faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    # 绘制规格
    drawSpec = mpdraw.DrawingSpec(thickness=1, circle_radius=1)

    Pre_time = 0
    while True:
        res, img = cap.read()
        if not res:
            break
            
        # 添加镜像翻转
        img = cv2.flip(img, 1)  # 水平翻转图像，创建镜像效果
            
        img_rgb = cv2.cvtColor(img, code=cv2.COLOR_BGR2RGB)
        results = faceMesh.process(img_rgb)
        
        if results.multi_face_landmarks:
            for faceLms in results.multi_face_landmarks:
                # 绘制所有面部特征点
                mpdraw.draw_landmarks(img, faceLms, mpFaceMesh.FACEMESH_CONTOURS,
                                     drawSpec, drawSpec)
                
                # 获取关键点坐标用于判断头部方向
                h, w, c = img.shape
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
                elif y > 10:
                    head_pose_horizontal = "Right"
                else:
                    head_pose_horizontal = "Center"
                
                # 垂直方向判断（上下）- 修正方向
                if x > 10:  # 原来是 x < -10
                    head_pose_vertical = "Up"
                elif x < -10:  # 原来是 x > 10
                    head_pose_vertical = "Down"
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
                else:
                    # 其他情况，显示水平方向
                    head_pose = head_pose_horizontal
                
                # 显示头部方向 - 分开显示垂直和水平方向
                # 创建背景
                overlay = img.copy()
                # 使用矩形作为背景
                cv2.rectangle(overlay, (10, 20), (320, 220), (40, 40, 40), -1)
                alpha = 0.7  # 增加不透明度使文字更清晰
                img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
                
                # 添加标题栏
                cv2.rectangle(img, (10, 20), (320, 55), (70, 70, 70), -1)
                cv2.putText(img, "Head Pose Detection", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # 状态指示器 
                status_color = (0, 255, 0)  # 默认绿色
                if head_pose != "Center":
                    status_color = (0, 165, 255)  # 橙色，表示头部偏离中心
                cv2.circle(img, (300, 38), 10, status_color, -1)
                
                # 主方向显示
                cv2.putText(img, "Direction:", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                cv2.putText(img, f"{head_pose}", (120, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 使用方向指示符
                if head_pose == "Left":
                    cv2.putText(img, "<-", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif head_pose == "Right":
                    cv2.putText(img, "->", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif head_pose == "Up":
                    cv2.putText(img, "^", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif head_pose == "Down":
                    cv2.putText(img, "o", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif head_pose == "Center":
                    cv2.putText(img, "v", (250, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                # 添加细节区域标题
                cv2.putText(img, "Details:", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                
                # 分开显示水平和垂直方向信息 
                cv2.putText(img, "Horizontal:", (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
                cv2.putText(img, f"{head_pose_horizontal}", (140, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
                
                cv2.putText(img, "Vertical:", (40, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
                cv2.putText(img, f"{head_pose_vertical}", (140, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 150, 100), 2)
                
                # 角度区域标题
                cv2.putText(img, "Angles:", (20, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                
                # 显示角度信息 
                cv2.putText(img, f"X: {int(x)}", (90, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(img, f"Y: {int(y)}", (160, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                # 目前基于2D，不需要z轴
                # cv2.putText(img, f"Z: {int(z)}", (240, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
                # 绘制坐标轴 
                nose_3d_projection, jacobian = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rot_vec, trans_vec, cam_matrix, dist_matrix)
                p1 = (int(face_2d[0][0]), int(face_2d[0][1]))
                p2 = (int(nose_3d_projection[0][0][0]), int(nose_3d_projection[0][0][1]))
                

        cv2.imshow('Head Pose Detection', img)  
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

face_detect()