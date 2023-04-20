# ChatGPT Wizard
![ss](ss.png)

A tool for using ChatGPT with Python through the API.
PySimpleGUI is used for the graphical user interface (GUI).

The official library is used.
https://platform.openai.com/docs/libraries

## Usage Instructions
1. Obtain an API key from https://platform.openai.com/
2. Create an environment variable named "chatGPT" and set the API key as its value
3. Clone `main.py` and install the libraries from the requirements

### Note
The API key is obtained from the environment variable as follows:
If you are not familiar with environment variables, you can directly insert the API key, and it will still work.

    openai.api_key = os.getenv("chatGPT")
## How to Use
### Request Details
You can select what you want to request. 
The purpose is to omit the prompt sentence. 
You can customize the following list by changing it:

    SYSTEM_CHOICES =["Not specified",
        "Spelling and grammar check",
        "Creating VBA code",
        "Creating Python code",
        "Refactoring",
        "Translation into English"]   
### Chat
Enter the conversation content in the upper box and press "Send"
### Edit
Enter the number displayed before "< user >" and press "Edit"
A dialog for editing will appear