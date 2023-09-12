import base64
import json


def vmess_to_clash(vmess_url):
    """
    将 VMess URL 转换为 Clash 配置。

    Args:
        vmess_url (str): VMess URL。

    Returns:
        dict: Clash 配置。
    """

    # 检查 URL 是否以 vmess:// 开头
    if not vmess_url.startswith("vmess://"):
        raise ValueError("Invalid VMess URL")

    # 解码 base64 编码的 json 字符串
    vmess_data = base64.b64decode(vmess_url[8:])
    vmess_config = json.loads(vmess_data)

    # 创建 Clash 配置
    clash_config = {
        "proxy": {
            "name": "VMess",
            "type": "vmess",
            "host": vmess_config["host"],
            "port": vmess_config["port"],
            "uuid": vmess_config["uuid"],
            # 如果有 cipher 字段，则使用相同的加密方式，否则使用 auto
            "security": vmess_config.get("cipher", "auto"),
            # 如果有 tlsSettings 字段，则启用 TLS，否则不启用
            "tls": "tlsSettings" in vmess_config,
        }
    }

    # 如果有 password 字段，则添加到 Clash 配置中
    if "password" in vmess_config:
        clash_config["proxy"]["password"] = vmess_config["password"]

    return clash_config


if __name__ == "__main__":
    vmess_url = "vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIue+juWbvSIsDQogICJhZGQiOiAiZG9uZ3RhaXdhbmcyLmNvbSIsDQogICJwb3J0IjogIjQ0MyIsDQogICJpZCI6ICI4N2E5NTUyMi05ODVjLTRhMTctYWZlYS05YjdkNzIwOGJjZTUiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIjMuZnJlZWsxLnh5eiIsDQogICJwYXRoIjogIi9kb25ndGFpd2FuZy5jb20iLA0KICAidGxzIjogInRscyIsDQogICJzbmkiOiAiIiwNCiAgImFscG4iOiAiIg0KfQ=="
    clash_config = vmess_to_clash(vmess_url)

    print(clash_config)
