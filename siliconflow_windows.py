import pyperclip
import time
import tkinter as tk
from tkinter import messagebox
import requests
from pynput import mouse

# API相关设置
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer sk-klawqyoodcrpleslhlotszwsqwvqsuugwxgozemrxiaeadmm"
}

def get_response(user_message, type_):
    payload = {
        "model": "Qwen/Qwen2-7B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "max_tokens": 4096
    }
    if type_ == "translation":
        payload["messages"][0]["content"] = f"请将这段文本翻译成中文: {user_message}"
    elif type_ == "explanation":
        payload["messages"][0]["content"] = f"请解释这段文本的含义: {user_message}"

    response = requests.post(url, json=payload, headers=headers)
    return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')

def show_menu(selected_text):
    def translate():
        result = get_response(selected_text, "translation")
        messagebox.showinfo("Translation", result)

    def explain():
        result = get_response(selected_text, "explanation")
        messagebox.showinfo("Explanation", result)

    # 使用 `tk.Tk()` 作为根窗口并隐藏它
    root = tk.Tk()
    root.withdraw()

    # 使用 `tk.Toplevel` 作为菜单的父窗口
    menu_window = tk.Toplevel(root)
    menu_window.withdraw()  # 隐藏窗口
    menu_window.overrideredirect(True)  # 去掉窗口装饰
    menu = tk.Menu(menu_window, tearoff=0)

    menu.add_command(label="Translate", command=lambda: [menu_window.destroy(), translate()])
    menu.add_command(label="Explain", command=lambda: [menu_window.destroy(), explain()])

    # 获取当前鼠标坐标并显示菜单
    menu_window.geometry(f"+{root.winfo_pointerx()}+{root.winfo_pointery()}")
    menu_window.deiconify()  # 显示窗口
    menu.post(root.winfo_pointerx(), root.winfo_pointery())

    # 确保菜单窗口关闭时根窗口也销毁
    menu_window.bind("<FocusOut>", lambda e: menu_window.destroy())
    root.mainloop()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left and not pressed:
        time.sleep(0.1)  # 确保文本已经被选中
        selected_text = pyperclip.paste()
        if selected_text.strip():
            show_menu(selected_text)

def main():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    main()