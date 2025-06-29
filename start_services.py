"""
启动前后端服务的脚本
"""
import os
import subprocess
import sys
import time
import shutil

def find_executable(name):
    """查找可执行文件在系统中的完整路径"""
    return shutil.which(name)

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    # 保存当前工作目录
    original_dir = os.getcwd()
    
    # 切换到Backend目录
    os.chdir("Backend")
    
    # 设置PYTHONPATH环境变量，让Python能找到Backend目录
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = os.path.dirname(original_dir)
    
    # 使用绝对导入而非相对导入
    backend_process = subprocess.Popen(
        ["python", "-c", """
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uvicorn
if __name__ == '__main__':
    uvicorn.run('Backend.main:app', host='0.0.0.0', port=8000, reload=True)
"""],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=backend_env
    )
    print("后端服务已启动，访问 http://localhost:8000")
    return backend_process

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    frontend_dir = os.path.join(os.path.dirname(os.getcwd()), "Frontend")
    if os.path.exists(frontend_dir):
        os.chdir(frontend_dir)
    else:
        os.chdir("../Frontend")
    
    print(f"前端工作目录: {os.getcwd()}")
    
    # 检查package.json是否存在
    if not os.path.exists("package.json"):
        print("错误: Frontend目录中找不到package.json文件")
        print(f"当前工作目录: {os.getcwd()}")
        return None
    
    # 查找npm可执行文件
    npm_path = find_executable("npm")
    if not npm_path:
        print("错误: 找不到npm命令。请确保Node.js已安装并且npm在系统PATH中。")
        return None
        
    print(f"使用的npm路径: {npm_path}")
    
    try:
        frontend_process = subprocess.Popen(
            [npm_path, "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("前端服务已启动")
        return frontend_process
    except Exception as e:
        print(f"启动前端时出错: {str(e)}")
        return None

def main():
    """主函数"""
    # 确保在项目根目录运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"工作目录: {os.getcwd()}")
    
    # 启动后端
    backend_process = start_backend()
    
    # 等待几秒，确保后端启动
    time.sleep(5)
    
    # 启动前端
    frontend_process = start_frontend()
    
    if frontend_process is None:
        print("前端启动失败，正在关闭后端...")
        backend_process.terminate()
        return
    
    try:
        # 保持脚本运行
        while True:
            # 检查进程是否仍在运行
            if backend_process.poll() is not None:
                print("后端服务已停止运行，退出中...")
                break
            if frontend_process.poll() is not None:
                print("前端服务已停止运行，退出中...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n关闭服务...")
    finally:
        # 确保进程被终止
        if backend_process.poll() is None:
            backend_process.terminate()
        if frontend_process.poll() is None:
            frontend_process.terminate()
        print("服务已关闭")

if __name__ == "__main__":
    main() 