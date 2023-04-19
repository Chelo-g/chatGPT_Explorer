# ChatGPT Explorer
![ss](ss.png)

APIを使用し、PythonにてChatGPTを使うツールです
GUI化はPySimpleGUIを使用しています。

公式のライブラリを使用しています。
https://platform.openai.com/docs/libraries

## 使用手順
1. https://platform.openai.com/  よりAPIkeyを取得
2. 環境変数chatGPTを作成. APIkeyを値として入れる 
3. main.pyをcloneしてrequirementsのライブラリを入れる

### 補足 
API keyは下記のように、環境変数から行っています  
環境変数周りがよくわからなければ、APIkeyをそのまま入れても動きます

    openai.api_key = os.getenv("chatGPT")
## 使い方
### 会話する
上の枠に会話内容を入力、送信を押してください
### 修正
< user >の前に表示されている数字を入力し、修正を押してください  
修正を行うためのダイアログが表示されます
