import os
import subprocess

# 获取当前脚本所在的目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 指定要运行的三个文件名
scripts_to_run = ["account.py", "storage_query.py", "identify.py"]
    
# 存储所有子进程的列表
processes = []

# 遍历指定的文件列表
for filename in scripts_to_run:
    file_path = os.path.join(current_dir, filename)
    print(f"Starting {filename}...")

    # 使用 subprocess.Popen 启动子进程
    process = subprocess.Popen(
        ["python", file_path],
        cwd=current_dir,  # 确保工作目录正确
        shell=True
    )
    processes.append(process)

# 等待所有子进程完成
for process in processes:
    process.wait()