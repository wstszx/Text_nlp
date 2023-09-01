import json
import requests

def parse_vmess(json_data):
  """
  解析 JSON 格式的 vmess 链接，返回一个字典

  Args:
    json_data: JSON 格式的 vmess 链接

  Returns:
    一个字典，包含 vmess 链接的所有信息
  """

  vmess_data = json.loads(json_data)
  return vmess_data

def convert_vmess_to_clash(json_data):
  """
  将 JSON 格式的 vmess 链接转换成 clash 的订阅内容

  Args:
    json_data: JSON 格式的 vmess 链接

  Returns:
    clash 的订阅内容
  """

  vmess_data = parse_vmess(json_data)
  return {
    "name": vmess_data["name"],
    "type": "vmess",
    "servers": [
      {
        "address": vmess_data["addr"],
        "port": vmess_data["port"],
        "uuid": vmess_data["uuid"],
        "alterid": vmess_data["alterid"],
        "cipher": vmess_data["cipher"],
        "auth": vmess_data["auth"],
        "tls": vmess_data["tls"],
        "udp": vmess_data["udp"],
      }
    ],
  }

if __name__ == "__main__":
  json_data = "vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIue+juWbvSIsDQogICJhZGQiOiAiZG9uZ3RhaXdhbmcyLmNvbSIsDQogICJwb3J0IjogIjQ0MyIsDQogICJpZCI6ICI4N2E5NTUyMi05ODVjLTRhMTctYWZlYS05YjdkNzIwOGJjZTUiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIjMuZnJlZWsxLnh5eiIsDQogICJwYXRoIjogIi9kb25ndGFpd2FuZy5jb20iLA0KICAidGxzIjogInRscyIsDQogICJzbmkiOiAiIiwNCiAgImFscG4iOiAiIg0KfQ=="
  subscription = convert_vmess_to_clash(json_data)
  print(json.dumps(subscription))
