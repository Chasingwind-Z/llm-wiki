#!/usr/bin/env bash
# 安装/更新 macOS Finder 快捷操作「存入知识库」（右键菜单 → 快速操作）。
# 行为：选中文件/文件夹 → 右键 → 存入知识库 → 弹窗选分类（动态列出 kb/ 下
# 全部分类 + capture 兜底）→ 选方式（软链接=活来源 / 复制=快照）→ 完成通知。
# 幂等可重跑；卸载：rm -rf ~/Library/Services/存入知识库.workflow
set -euo pipefail
cd "$(dirname "$0")/.."
KB_DIR="$(pwd)"

WF="$HOME/Library/Services/存入知识库.workflow"
mkdir -p "$WF/Contents"

# 快捷操作里跑的 shell（zsh，文件路径作为参数传入）
read -r -d '' PAYLOAD <<'ZSH' || true
KB="__KB_DIR__"
[ -d "$KB/kb" ] || exit 0
# 动态分类列表
opts=""
for d in "$KB"/kb/*/; do c=$(basename "$d"); opts+="\"$c\","; done
opts+="\"capture（还没想好，稍后分拣）\""
choice=$(osascript -e "choose from list {$opts} with title \"知识库\" with prompt \"存入哪个知识库？\"" 2>/dev/null)
[ "$choice" = "false" ] || [ -z "$choice" ] && exit 0
if [[ "$choice" == capture* ]]; then
  for f in "$@"; do cp -R "$f" "$KB/capture/"; done
  dest="capture"
else
  mode=$(osascript -e 'choose from list {"软链接（活来源：改原文会提醒同步）","复制（快照：入库后与原文无关）"} with title "知识库" with prompt "以什么方式存入？"' 2>/dev/null)
  [ "$mode" = "false" ] || [ -z "$mode" ] && exit 0
  if [[ "$mode" == 软链接* ]]; then
    /usr/bin/python3 "$KB/scripts/link_raw.py" "$choice" "$@" >/dev/null 2>&1 || true
  else
    for f in "$@"; do cp -R "$f" "$KB/kb/$choice/raw/"; done
  fi
  dest="$choice"
fi
osascript -e "display notification \"$# 项已存入 $dest（下次开工会提醒 ingest）\" with title \"知识库\"" 2>/dev/null
ZSH
PAYLOAD="${PAYLOAD/__KB_DIR__/$KB_DIR}"

WF_PATH="$WF" PAYLOAD="$PAYLOAD" python3 - <<'PY'
import os, plistlib, uuid

wf = os.environ["WF_PATH"]; cmd = os.environ["PAYLOAD"]

info = {
    "NSServices": [{
        "NSMenuItem": {"default": "存入知识库"},
        "NSMessage": "runWorkflowAsService",
        "NSRequiredContext": {"NSApplicationIdentifier": "com.apple.finder"},
        "NSSendFileTypes": ["public.item"],
    }]
}
with open(f"{wf}/Contents/Info.plist", "wb") as f:
    plistlib.dump(info, f)

u = [str(uuid.uuid4()).upper() for _ in range(3)]
doc = {
    "AMApplicationBuild": "528", "AMApplicationVersion": "2.10", "AMDocumentVersion": "2",
    "actions": [{
        "action": {
            "AMAccepts": {"Container": "List", "Optional": True,
                          "Types": ["com.apple.cocoa.path"]},
            "AMActionVersion": "2.0.3",
            "AMApplication": ["Automator"],
            "AMParameterProperties": {k: {} for k in
                ("COMMAND_STRING", "CheckedForUserDefaultShell", "inputMethod", "shell", "source")},
            "AMProvides": {"Container": "List", "Types": ["com.apple.cocoa.string"]},
            "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
            "ActionName": "运行 Shell 脚本",
            "ActionParameters": {
                "COMMAND_STRING": cmd,
                "CheckedForUserDefaultShell": False,
                "inputMethod": 1,          # 作为参数传入
                "shell": "/bin/zsh",
                "source": "",
            },
            "BundleIdentifier": "com.apple.RunShellScript",
            "CFBundleVersion": "2.0.3",
            "CanShowSelectedItemsWhenRun": False, "CanShowWhenRun": True,
            "Category": ["AMCategoryUtilities"],
            "Class Name": "RunShellScriptAction",
            "InputUUID": u[0], "OutputUUID": u[1], "UUID": u[2],
            "Keywords": [], "ShowWhenRun": False,
            "UnlocalizedApplications": ["Automator"],
            "arguments": {"0": {"default value": 0, "name": "inputMethod",
                                "required": "0", "type": "0", "uuid": "0"}},
            "isViewVisible": True,
        },
    }],
    "connectors": {},
    "workflowMetaData": {
        "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
        "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
        "serviceProcessesInput": 0,
        "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
    },
}
with open(f"{wf}/Contents/document.wflow", "wb") as f:
    plistlib.dump(doc, f)
print("✓ 已写入", wf)
PY

plutil -lint "$WF/Contents/Info.plist" >/dev/null && plutil -lint "$WF/Contents/document.wflow" >/dev/null && echo "✓ plist 校验通过"
# 让 Finder 服务注册刷新
/System/Library/CoreServices/pbs -update 2>/dev/null || true
echo
echo "用法：Finder 选中文件/文件夹 → 右键 → 快速操作 →「存入知识库」"
echo "若菜单里没出现：系统设置 → 隐私与安全性 → 扩展 → Finder（勾选它），或注销重登。"
