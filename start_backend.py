"""
启动后端服务的简化脚本
"""
import os
import sys
from multiprocessing import freeze_support

# 获取当前脚本所在目录作为项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

def main():
    # 将项目根目录添加到Python路径
    sys.path.insert(0, project_root)

    # 设置工作目录为Backend目录
    backend_dir = os.path.join(project_root, 'Backend')
    os.chdir(backend_dir)

    # 添加当前工作目录到PATH环境变量，以便找到模块
    os.environ["PYTHONPATH"] = project_root

    try:
        import uvicorn
        print("启动后端服务...")
        print(f"项目根目录: {project_root}")
        print(f"工作目录: {os.getcwd()}")
        print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
        
        # 启动应用
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError as e:
        print(f"错误: 未找到必要的模块: {e}")
        print("请运行以下命令安装:")
        print("pip install uvicorn fastapi")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    freeze_support()
    main() 