import openai
import json
import os
import PySimpleGUI as sg

# 環境変数で以下を登録、もしくはAPIKEYに書き換えてください
# 変数 chatGPT
# 値 https://platform.openai.com/にて取得したAPI KEY
API_KEY = os.getenv("chatGPT")

SYSTEM_CHOICES = [
    "指定しない",
    "誤字脱字チェック",
    "VBAコード作成",
    "Pythonコード作成",
    "リファクタリング",
    "英語に翻訳"
]


# その他の関数定義
def save_chat_history(chat):
    save_path = sg.popup_get_file("チャット履歴を保存するファイルを選択してください", save_as=True, no_window=True)
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(chat, f, ensure_ascii=False, indent=2)
        sg.popup("チャット履歴が保存されました: {}".format(save_path))
        return 1
    else:
        sg.popup("チャット履歴の保存がキャンセルされました")
        return 0


def load_chat_history(filename=None):
    if not filename:
        filename = "chat_history.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def modify_chat(chat, index, new_content):
    if 0 <= index < len(chat):
        chat[index]["content"] = new_content
        return True
    return False


def update_output(chat, window):
    updated_chat = "\n".join([f"{i}: <{msg['role']}> \n{msg['content']}\n{'-' * 80}" if msg[
                                                                                            'role'] == 'assistant' else f"{i}: <{msg['role']}>\n {msg['content']}"
                              for i, msg in enumerate(chat)])
    window["output"].update(updated_chat + "\n")


def calculate_cost(model, tokens):
    if model == "gpt-3.5-turbo":
        cost_per_1k_tokens = 0.002
    elif model == "gpt-4":
        cost_per_1k_tokens = 0.03
    else:
        raise ValueError("Invalid model")

    cost = (tokens / 1000) * cost_per_1k_tokens
    return cost


def send_message(values, chat, total_tokens, window):
    user_input = values["content"] if "content" in values else values["input"].rstrip()
    if len(chat) == 0 and values["system_combo"] != '指定しない':
        selected_system_message = values["system_combo"]
        chat.append({"role": "system", "content": selected_system_message})
    chat.append({"role": "user", "content": user_input})
    model = values["model"]

    sg.popup_no_wait("ChatGPTからの応答を待っています...", auto_close=True)

    try:
        response = openai.ChatCompletion.create(model=model, messages=chat)
    except openai.error.APIConnectionError:
        sg.popup("OpenAI APIとの通信中にエラーが発生しました。インターネット接続を確認してください。")
        return chat, total_tokens
    msg = response["choices"][0]["message"]["content"].lstrip()
    current_tokens = response["usage"]["total_tokens"]
    total_tokens += current_tokens
    chat.append({"role": "assistant", "content": msg})
    update_output(chat, window)

    window["input"].update("")
    window["current_tokens_used"].update(str(current_tokens))
    window["total_tokens_used"].update(str(total_tokens))

    cost = calculate_cost(model, total_tokens)
    window["total_cost"].update(f"${cost:.4f}")

    return chat, total_tokens


def handle_send_event(values, chat, total_tokens, window):
    return send_message(values, chat, total_tokens, window)


def handle_modify_event(values, chat, total_tokens, window):
    try:
        modify_index = int(values["modify_index"])
        if 0 <= modify_index < len(chat) and chat[modify_index]["role"] == "user":
            current_content = chat[modify_index]["content"]
            response = sg.popup_yes_no(f"現在の内容：\n{current_content}\n\nこの内容を修正しますか？")
            if response == "Yes":
                new_content = sg.popup_get_text("新しい内容を入力してください：")
                if new_content is not None:
                    # modify_chat(chat, modify_index, new_content)
                    chat = chat[:modify_index]  # 修正以降の会話を削除
                    update_output(chat, window)
                    sg.popup("会話が修正されました。\n\n修正後の内容：\n{}".format(new_content))

                    # 修正後の内容でChatGPTに送信する
                    values["content"] = new_content
                    chat, total_tokens = send_message(values, chat, total_tokens, window)
        else:
            sg.popup("無効なインデックスです。ユーザーの発言のみ修正できます。")
    except ValueError:
        sg.popup("無効なインデックスです。")

    return chat


def main():
    sg.theme('DarkGray11')
    openai.api_key = API_KEY
    total_tokens = 0
    current_tokens = 0

    # PySimpleGUIのレイアウト
    layout = [
        [sg.Multiline("ここに入力してください\n", key="input", size=(80, 5))],
        [sg.Text("依頼内容:"),
         sg.Combo(SYSTEM_CHOICES, size=(30, len(SYSTEM_CHOICES)), key="system_combo", default_value="指定しない",
                  enable_events=True)],
        [sg.Text("モデル："),
         sg.Combo(["gpt-3.5-turbo", "gpt-4"], key="model", default_value="gpt-3.5-turbo", readonly=True),
         sg.Button("送信"), sg.Button("新しい会話"), sg.Button("終了")],
        [sg.Text("今回の会話で使用したトークン数："), sg.Text("0", key="current_tokens_used", size=(10, 1))],
        [sg.Text("累計使用したトークン数："), sg.Text("0", key="total_tokens_used", size=(10, 1))],
        [sg.Text("累計利用料金："), sg.Text("$0.0000", key="total_cost", size=(10, 1))],
        [sg.Text("保存するファイル名："), sg.Input(key="save_filename", default_text="chat_history.json"), sg.Button("保存")],
        [sg.Text("読み込むファイル名："), sg.Input(key="load_filename", default_text="chat_history.json"),
         sg.Button("読み込む")],
        [sg.Text("修正する会話のインデックス："), sg.Input(key="modify_index", size=(5, 1)), sg.Button("修正")],
        [sg.Multiline("", key="output", size=(80, 20), disabled=True, autoscroll=True)]
    ]

    window = sg.Window("chatGPT Wizard", layout)
    chat = []

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "終了":
            break
        elif event == "送信":
            chat, total_tokens = handle_send_event(values, chat, total_tokens, window)
        elif event == "保存":
            save_chat_history(chat)
            sg.popup("会話履歴が保存されました。")
        elif event == "読み込む":
            load_file_path = sg.popup_get_file("ファイルを選択してください")
            if load_file_path is not None:
                chat = load_chat_history(load_file_path)
                update_output(chat, window)
                sg.popup("会話が読み込まれました。")
        elif event == "修正":
            chat = handle_modify_event(values, chat, total_tokens, window)
        elif event == "新しい会話":
            if chat:
                response = sg.popup_yes_no("現在の会話を保存しますか？")
                if response == "Yes":
                    if save_chat_history(chat) == 0:
                        continue
                else:
                    response = sg.popup_yes_no("保存せず初期状態に戻して良いですか？")
                    if response == "No":
                        continue
            chat = []
            update_output(chat, window)
            window["current_tokens_used"].update("0")
            current_tokens = 0
    window.close()


if __name__ == "__main__":
    main()
