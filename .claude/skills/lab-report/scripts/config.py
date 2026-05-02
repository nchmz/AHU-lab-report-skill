"""
管理 lab-report skill 的配置文件。

用法：
    python config.py get-python-env
    python config.py set-python-env <cmd>
    python config.py get-report-title <subject>
    python config.py add-report <subject> <title>

配置文件路径：.claude/skills/lab-report/config.json
"""

import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

CONFIG_PATH = Path(__file__).parent.parent / "config.json"
# .claude/skills/lab-report/scripts/ -> .claude/skills/lab-report/ -> .claude/skills/ -> .claude/ -> project root
REPORTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "reports"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_python_env():
    config = load_config()
    env = config.get("python_env")
    if env and env.get("cmd"):
        print(env["cmd"])
    else:
        print("")


def set_python_env(cmd: str):
    config = load_config()
    config["python_env"] = {"cmd": cmd}
    save_config(config)
    print(f"Python env saved: {cmd}")


def get_report_title(subject: str):
    """根据科目名生成下一个实验报告标题。

    扫描 reports/ 目录下已有的同科目文件夹，确定下一个编号。
    中文数字序列：一、二、三、四、五、六、七、八、九、十
    """
    config = load_config()
    reports = config.get("reports", {})

    # 从配置和实际目录两方面获取已有报告
    existing = set()
    if subject in reports:
        for r in reports[subject]:
            existing.add(r.get("title", ""))

    # 同时扫描 reports 目录，找出以该科目开头的文件夹
    if REPORTS_DIR.exists():
        for d in REPORTS_DIR.iterdir():
            if d.is_dir() and d.name.startswith(subject):
                existing.add(d.name)

    # 匹配 "{subject}实验N" 格式（N 为阿拉伯数字）
    import re
    used_indices = set()
    pattern = re.compile(r"^" + re.escape(subject) + r"实验(\d+)$")
    for title in existing:
        m = pattern.match(title)
        if m:
            used_indices.add(int(m.group(1)))

    # 找下一个未使用的编号
    next_idx = 1
    while next_idx in used_indices:
        next_idx += 1

    title = f"{subject}实验{next_idx}"
    print(title)


def add_report(subject: str, title: str):
    config = load_config()
    if "reports" not in config:
        config["reports"] = {}
    if subject not in config["reports"]:
        config["reports"][subject] = []

    # 避免重复添加
    titles = [r["title"] for r in config["reports"][subject]]
    if title not in titles:
        config["reports"][subject].append({"title": title})

    save_config(config)
    print(f"Report added: {subject} -> {title}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python config.py <command> [args...]")
        print("Commands: get-python-env, set-python-env, get-report-title, add-report")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "get-python-env":
        get_python_env()
    elif cmd == "set-python-env":
        if len(sys.argv) < 3:
            print("Usage: python config.py set-python-env <cmd>")
            sys.exit(1)
        set_python_env(sys.argv[2])
    elif cmd == "get-report-title":
        if len(sys.argv) < 3:
            print("Usage: python config.py get-report-title <subject>")
            sys.exit(1)
        get_report_title(sys.argv[2])
    elif cmd == "add-report":
        if len(sys.argv) < 4:
            print("Usage: python config.py add-report <subject> <title>")
            sys.exit(1)
        add_report(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
