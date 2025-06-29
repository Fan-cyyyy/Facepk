"""
启动前端服务的简化脚本
"""
import os
import sys
import subprocess
import shutil

def find_executable(name):
    """查找可执行文件在系统中的完整路径"""
    return shutil.which(name)

def main():
    """主函数"""
    # 确保在项目根目录运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 切换到Frontend目录
    frontend_dir = os.path.join(script_dir, "Frontend")
    if os.path.exists(frontend_dir):
        os.chdir(frontend_dir)
        print(f"已切换到前端目录: {os.getcwd()}")
    else:
        print(f"错误: 找不到前端目录: {frontend_dir}")
        return
    
    # 检查package.json是否存在
    if not os.path.exists("package.json"):
        print("错误: Frontend目录中找不到package.json文件")
        return
    
    # 查找npm可执行文件
    npm_path = find_executable("npm")
    if not npm_path:
        print("错误: 找不到npm命令。请确保Node.js已安装并且npm在系统PATH中。")
        print("如果已安装Node.js，请尝试使用完整路径:")
        print("  如: C:\\Program Files\\nodejs\\npm.cmd run dev")
        return
        
    print(f"使用的npm路径: {npm_path}")
    
    # 直接在控制台运行命令，而不是创建子进程
    try:
        print("启动前端服务...")
        print("按Ctrl+C可以停止服务")
        
        # 直接执行npm命令
        npm_cmd = [npm_path, "run", "dev"]
        process = subprocess.run(npm_cmd)
        
        if process.returncode != 0:
            print(f"前端服务退出，返回码: {process.returncode}")
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动前端时出错: {str(e)}")

if __name__ == "__main__":
    main() 