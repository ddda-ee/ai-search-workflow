# -*- coding: utf-8 -*-
"""交互式大模型配置工具。

像 SwitchCC 一样：选择服务商、填写 API Key、选择模型，
配置会保存到 .env，并支持保存多套配置快速切换。
"""

import getpass
import json
from pathlib import Path

from dotenv import dotenv_values

from config.providers import PROVIDERS, PROVIDER_MAP


# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent
ENV_FILE = ROOT_DIR / ".env"
PROFILES_FILE = ROOT_DIR / "config" / "llm_profiles.json"


# =========================
# 配置文件的读写
# =========================

def load_profiles() -> dict:
    """读取已保存的多套配置。"""
    if not PROFILES_FILE.exists():
        return {"active": None, "profiles": {}}
    try:
        data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"active": None, "profiles": {}}
    return data


def save_profiles(data: dict) -> None:
    """保存多套配置到本地 JSON 文件。"""
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_env() -> dict:
    """读取 .env 中已有的键值对。"""
    return dotenv_values(ENV_FILE)


def write_env(values: dict) -> None:
    """把键值写入 .env，保留原有注释和其他键。"""
    lines = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()

    written = set()
    result = []

    # 先更新已存在的键
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(line)
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                result.append(f'{key} = "{values[key]}"')
                written.add(key)
                continue
        result.append(line)

    # 追加还没写入的新键
    for key, value in values.items():
        if key not in written:
            result.append(f'{key} = "{value}"')

    ENV_FILE.write_text("\n".join(result) + "\n", encoding="utf-8")


# =========================
# 交互辅助函数
# =========================

def choose_number(prompt: str, max_choice: int) -> int:
    """让用户输入一个序号（0 到 max_choice），返回用户输入的数字。

    max_choice 表示最大的合法序号；0 通常表示退出或返回。
    """
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            choice = int(raw)
            if 0 <= choice <= max_choice:
                return choice
        print(f"输入无效，请输入 0 到 {max_choice} 之间的数字。")


def input_api_key(provider: dict) -> str:
    """输入 API Key，本地服务可以不填。"""
    if not provider.get("api_key_env"):
        key = input("本地服务一般不需要 Key，可直接回车：").strip()
        return key or "local"
    while True:
        try:
            key = getpass.getpass("请输入 API Key（输入时不显示）：").strip()
        except (EOFError, KeyboardInterrupt):
            key = input("请输入 API Key：").strip()
        if key:
            return key
        print("API Key 不能为空，请重新输入。")


def input_model(provider: dict, old_model: str = "") -> str:
    """选择或输入模型名。"""
    models = provider.get("default_models") or []
    if models:
        print("\n可选模型：")
        for i, name in enumerate(models, start=1):
            mark = "  (当前)" if name == old_model else ""
            print(f"  {i}. {name}{mark}")
        print(f"  {len(models) + 1}. 手动输入模型名")
        choice = choose_number("请选择模型：", len(models) + 1)
        if 1 <= choice <= len(models):
            return models[choice - 1]
    return input("请输入模型名：").strip()


def mask_key(key: str) -> str:
    """对 API Key 做脱敏显示。"""
    if not key or key == "local":
        return key
    if len(key) <= 6:
        return "***"
    return f"{key[:3]}...{key[-3:]}"


# =========================
# 配置动作
# =========================

def build_profile(provider_key: str, old: dict = None) -> dict:
    """引导用户配置一个 profile。"""
    provider = PROVIDER_MAP[provider_key]
    old = old or {}

    print(f"\n已选择服务商：{provider['name']}")

    # base_url
    default_base = old.get("base_url") or provider.get("base_url") or ""
    base_url = input(
        f"接口地址 Base URL（回车使用默认 {default_base or '请填写'}）："
    ).strip() or default_base
    if not base_url:
        print("Base URL 不能为空。")
        return None

    # model
    model = input_model(provider, old.get("model", ""))

    # api key
    api_key = input_api_key(provider)

    return {
        "provider": provider_key,
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
    }


def apply_profile(profile: dict, profile_name: str, data: dict) -> None:
    """把配置写入 .env，并标记为当前激活。"""
    write_env({
        "LLM_PROVIDER": profile["provider"],
        "MODEL_NAME": profile["model"],
        "LLM_BASE_URL": profile["base_url"],
        "LLM_API_KEY": profile["api_key"],
    })
    data["active"] = profile_name
    save_profiles(data)


def create_profile(data: dict) -> None:
    """新增一套配置。"""
    print("\n=== 新增配置 ===")
    print("可选服务商：")
    for i, p in enumerate(PROVIDERS, start=1):
        print(f"  {i}. {p['name']}")
    print(f"  {len(PROVIDERS) + 1}. 返回")
    choice = choose_number("请选择服务商：", len(PROVIDERS) + 1)
    if choice == len(PROVIDERS) + 1:
        return
    provider = PROVIDERS[choice - 1]
    profile = build_profile(provider["key"])
    if profile is None:
        return

    while True:
        name = input("给这套配置起个名字（如 deepseek主用）：").strip()
        if not name:
            print("名字不能为空。")
            continue
        if name in data["profiles"]:
            confirm = input(f"配置 {name} 已存在，覆盖吗？(y/n)：").strip().lower()
            if confirm == "y":
                break
            continue
        break

    data["profiles"][name] = profile
    apply_profile(profile, name, data)
    print(f"\n已保存并切换到配置：{name}")
    print_profile(name, profile)


def switch_profile(data: dict) -> None:
    """切换已有配置。"""
    profiles = data["profiles"]
    if not profiles:
        print("\n还没有保存过配置，请先新增配置。")
        return
    names = list(profiles.keys())
    print("\n=== 切换配置 ===")
    for i, name in enumerate(names, start=1):
        p = profiles[name]
        active = "  (当前)" if data["active"] == name else ""
        print(f"  {i}. {name}  [{PROVIDER_MAP[p['provider']]['name']} / {p['model']}]{active}")
    print(f"  {len(names) + 1}. 返回")
    choice = choose_number("请选择要切换到的配置：", len(names) + 1)
    if choice == len(names) + 1:
        return
    name = names[choice - 1]
    apply_profile(profiles[name], name, data)
    print(f"\n已切换到配置：{name}")


def delete_profile(data: dict) -> None:
    """删除一套配置。"""
    profiles = data["profiles"]
    if not profiles:
        print("\n没有可删除的配置。")
        return
    names = list(profiles.keys())
    print("\n=== 删除配置 ===")
    for i, name in enumerate(names, start=1):
        p = profiles[name]
        active = "  (当前)" if data["active"] == name else ""
        print(f"  {i}. {name}  [{PROVIDER_MAP[p['provider']]['name']} / {p['model']}]{active}")
    print(f"  {len(names) + 1}. 返回")
    choice = choose_number("请选择要删除的配置：", len(names) + 1)
    if choice == len(names) + 1:
        return
    name = names[choice - 1]
    confirm = input(f"确定删除配置 {name} 吗？(y/n)：").strip().lower()
    if confirm != "y":
        print("已取消。")
        return
    del data["profiles"][name]
    if data["active"] == name:
        data["active"] = None
    save_profiles(data)
    print(f"已删除配置：{name}")


def show_profiles(data: dict) -> None:
    """查看所有配置。"""
    profiles = data["profiles"]
    if not profiles:
        print("\n还没有保存过配置。")
        return
    print("\n=== 所有配置 ===")
    for name, p in profiles.items():
        active = "  (当前)" if data["active"] == name else ""
        print(f"- {name}{active}")
        print(f"    服务商: {PROVIDER_MAP[p['provider']]['name']}")
        print(f"    模型:   {p['model']}")
        print(f"    地址:   {p['base_url']}")
        print(f"    Key:    {mask_key(p['api_key'])}")


def print_profile(name: str, p: dict) -> None:
    """打印单个配置详情。"""
    print(f"    服务商: {PROVIDER_MAP[p['provider']]['name']}")
    print(f"    模型:   {p['model']}")
    print(f"    地址:   {p['base_url']}")
    print(f"    Key:    {mask_key(p['api_key'])}")


# =========================
# 主菜单
# =========================

def show_current(data: dict) -> None:
    """显示当前激活配置。"""
    active = data["active"]
    if active and active in data["profiles"]:
        p = data["profiles"][active]
        print(f"\n当前使用：{active}  [{PROVIDER_MAP[p['provider']]['name']} / {p['model']}]")
    else:
        env = read_env()
        provider = (env.get("LLM_PROVIDER") or "").strip()
        model = (env.get("MODEL_NAME") or "").strip()
        if provider:
            name = PROVIDER_MAP.get(provider, {}).get("name", provider)
            print(f"\n当前使用：{name} / {model}（来自 .env，尚未纳入配置管理）")
        else:
            print("\n当前未配置任何大模型。")


def main() -> None:
    data = load_profiles()
    while True:
        show_current(data)
        print("\n请选择操作：")
        print("  1. 新增配置（选服务商 + 填 Key + 选模型）")
        print("  2. 切换已有配置")
        print("  3. 删除配置")
        print("  4. 查看所有配置")
        print("  0. 退出")
        choice = choose_number("请输入序号：", 4)
        if choice == 0:
            print("再见！")
            break
        elif choice == 1:
            create_profile(data)
        elif choice == 2:
            switch_profile(data)
        elif choice == 3:
            delete_profile(data)
        elif choice == 4:
            show_profiles(data)


if __name__ == "__main__":
    main()