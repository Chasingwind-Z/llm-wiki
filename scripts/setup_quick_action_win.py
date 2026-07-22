#!/usr/bin/env python3
# 安装 Windows「发送到」菜单项：右键文件 → 发送到 → 存入知识库 → 弹出控制台选分类。
# macOS 的等价物是 bash scripts/setup-quick-action.sh（Finder 快速操作）。
# 幂等可重跑；卸载 = 删除「发送到」目录里的 存入知识库.bat。
# ⚠️ 逻辑已在 macOS 侧验证（quick_store.py 通用），但 .bat 封装尚未在真实 Windows
#    上实测，遇到问题请反馈（常见坑：python 不在 PATH、仓库路径含中文/空格）。
import os, sys

if os.name != "nt":
    print("此脚本仅用于 Windows；macOS 请用: bash scripts/setup-quick-action.sh")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if any(ord(ch) > 127 for ch in ROOT) or " " in ROOT:
    print(f"✗ 仓库路径含中文或空格（{ROOT}），.bat 会解析失败。请把仓库移到如 D:\\kb 再重跑。")
    sys.exit(1)

sendto = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo")
bat = os.path.join(sendto, "存入知识库.bat")
py = sys.executable or "python"
content = (
    "@echo off\r\n"
    "chcp 65001 >nul\r\n"
    f'"{py}" "{os.path.join(ROOT, "scripts", "quick_store.py")}" %*\r\n'
    "if errorlevel 1 pause\r\n"
    "timeout /t 2 >nul\r\n"
)
with open(bat, "w", encoding="ascii", newline="") as f:
    f.write(content)
print(f"✓ 已安装: {bat}")
print("用法：文件/文件夹上右键 → 发送到 → 存入知识库 → 按提示选分类和方式。")
