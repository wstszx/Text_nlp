import os
import re 
import time
import yaml
import requests
import schedule
import base64
import json
from flask import Flask, send_file

app = Flask(__name__)

url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"

@app.route('/')
def get_clash():
    get_and_write_clash()
    if os.path.exists('clash.yaml'):
        return send_file('clash.yaml', as_attachment=True)
    else:
        return 'Clash config not generated yet.'
        
def get_vmess_link():
    response = requests.get(url)
    content = response.text
    
    pattern = r"vmess://([\s\S]*?)</p>"
    vmess_links = re.findall(pattern, content)
    vmess = "vmess://" + vmess_links[0]

    return vmess

def decode_vmess(vmess):
    decodeVmessLink = base64.b64decode(vmess[8:])
    return json.loads(decodeVmessLink)

def generate_clash_config(decodeVmessLink):
    with open("template.yaml", encoding="utf-8") as f:
        file_data = f.read()

    yamlObject = yaml.load(file_data, yaml.FullLoader)

    proxies = yamlObject["proxies"][0]
    proxies["server"] = decodeVmessLink["add"]
    proxies["uuid"] = decodeVmessLink["id"] 
    proxies["ws-opts"]["path"] = decodeVmessLink["path"]
    yamlObject["proxies"][0] = proxies
    print(proxies)
    with open('clash.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(yamlObject, f)
        
def get_and_write_clash():
    vmess = get_vmess_link()
    print(vmess)
    decodeVmessLink = decode_vmess(vmess)
    generate_clash_config(decodeVmessLink)

def main():
    if not os.path.exists(r'vmess\clash.yaml'):
        get_and_write_clash()
        
    schedule.every(18).seconds.do(get_and_write_clash)
    
    app.run(host='0.0.0.0', port=5000)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()