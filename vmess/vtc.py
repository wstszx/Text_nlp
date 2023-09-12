import base64
import yaml
import json

vmessLink = r"vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIue+juWbvSIsDQogICJhZGQiOiAiZG9uZ3RhaXdhbmcyLmNvbSIsDQogICJwb3J0IjogIjQ0MyIsDQogICJpZCI6ICI4N2E5NTUyMi05ODVjLTRhMTctYWZlYS05YjdkNzIwOGJjZTUiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIjMuZnJlZWsxLnh5eiIsDQogICJwYXRoIjogIi9kb25ndGFpd2FuZy5jb20iLA0KICAidGxzIjogInRscyIsDQogICJzbmkiOiAiIiwNCiAgImFscG4iOiAiIg0KfQ=="
decodeVmessLink = base64.b64decode(vmessLink[8:])
decodeVmessLink = json.loads(decodeVmessLink)


with open("vmess/template.yaml", encoding="utf-8-sig") as file:
    file_data = file.read()

yamlObject = yaml.load(file_data, yaml.FullLoader) 
print("before----------------------------------------")
print(yamlObject["proxies"][0])

proxies = yamlObject["proxies"][0]
proxies["server"] = decodeVmessLink["add"]
proxies["uuid"] = decodeVmessLink["id"]
proxies["ws-opts"]["path"] = decodeVmessLink["path"]
print("after----------------------------------------")
print(proxies)
yamlObject["proxies"][0] = proxies

with open("SVTC.yaml", "w", encoding="utf-8-sig") as file:
    yaml.dump(yamlObject, file, encoding="utf-8-sig")
print("Success!")