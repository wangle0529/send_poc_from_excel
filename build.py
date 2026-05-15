import os
import subprocess
import shutil

def get_version():
    """从版本文件读取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), "static", "version.txt")
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"读取版本文件失败: {e}")
        return "unknown"

def build():
    """使用 PyInstaller 打包项目"""
    
    # 获取版本号
    version = get_version()
    app_name = f"WAF工具_{version}"
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 图标路径
    icon_path = os.path.join(project_root, "static", "favicon_256x256.ico")
    
    # 检查图标文件是否存在
    if not os.path.exists(icon_path):
        print(f"错误：图标文件不存在: {icon_path}")
        return False
    
    # PyInstaller 命令
    cmd = [
        "py",
        "-m",
        "PyInstaller",
        f"--name={app_name}",
        f"--icon={icon_path}",
        "--onefile",
        "--windowed",
        "--add-data=static;static",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "main.py"
    ]
    
    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    try:
        # 执行打包命令（不捕获输出，直接显示）
        result = subprocess.run(cmd, cwd=project_root, check=True)
        
        # 清理临时文件
        print("\n清理临时文件...")
        for folder in ["build", f"{app_name}.spec"]:
            folder_path = os.path.join(project_root, folder)
            if os.path.exists(folder_path):
                if os.path.isdir(folder_path):
                    shutil.rmtree(folder_path)
                else:
                    os.remove(folder_path)
                print(f"已删除: {folder}")
        
        print("\n打包完成！")
        print(f"可执行文件位置: {os.path.join(project_root, 'dist', f'{app_name}.exe')}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败！返回码: {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n错误：未找到 pyinstaller 命令")
        print("请先安装 pyinstaller: pip install pyinstaller")
        return False

if __name__ == "__main__":
    build()