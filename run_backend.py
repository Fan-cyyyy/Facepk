"""
启动后端服务的简化脚本
"""
import os
import sys
import subprocess

# 获取当前脚本所在目录
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'Backend')

# 检测Python可执行文件路径
def find_python_executable():
    # 尝试使用Python 3.10（uvicorn已安装的版本）
    python_paths = [
        r"C:\Users\Fancy\AppData\Local\Programs\Python\Python310\python.exe",
        "python3.10",
        "python3",
        "python"
    ]
    
    for path in python_paths:
        try:
            # 检查Python版本
            result = subprocess.run([path, "--version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            if result.returncode == 0:
                return path
        except:
            continue
    
    return None

def main():
    # 切换到Backend目录
    os.chdir(backend_dir)
    
    # 查找Python可执行文件
    python_exec = find_python_executable()
    if not python_exec:
        print("错误: 未找到合适的Python可执行文件。")
        sys.exit(1)
    
    print(f"使用Python: {python_exec}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查是否安装了uvicorn
    try:
        subprocess.run([python_exec, "-c", "import uvicorn"], check=True)
    except:
        print("错误: 未找到uvicorn模块。请安装必要的依赖:")
        print(f"{python_exec} -m pip install uvicorn fastapi sqlalchemy pydantic")
        sys.exit(1)
    
    # 启动FastAPI应用
    print("启动后端服务...")
    cmd = [python_exec, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动服务时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 