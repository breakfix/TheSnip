from argparse import ArgumentParser
from cryptography.fernet import Fernet
import urllib.request
import clipboard
import configparser
import secrets
import json
import os
import requests

def check_proxy():
    '''Platform independent
    check for system proxy
    '''

    proxy = urllib.request.getproxies()

    if proxy.get('https'):
        print("[+] Found system HTTPS proxy {}".format(proxy.get('https')))

    if proxy.get('http'):
        print("[+] Found system HTTP proxy {}".format(proxy.get('http')))
    
    return proxy

def generate():
    '''Generate settings.conf file
    '''

    print("[+] Generating 'settings.conf'")
    print("[+] Output file is: " + conf_path)

    # Check for system proxy
    proxy = check_proxy()

    channel_key = secrets.token_hex(20)
    encryption_key = Fernet.generate_key()
    channel_key = Fernet.generate_key()
    
    data = {
        'email': input('[+] Enter email address: '),
        'secret_key': channel_key.decode("utf-8"),
        'default_ttl': '604800'
    }

    response = requests.post('https://kvdb.io/', data=data, proxies=proxy)
    
    with open(conf_path, 'w') as outfile:
        outfile.write('[settings]' + '\n')
        outfile.write('channel: ' + response.text + '\n')
        outfile.write('channel_key: ' + channel_key.decode("utf-8") + '\n')
        outfile.write('encryption_key: ' + encryption_key.decode("utf-8") + '\n')
        outfile.write('proxy: ' + str(proxy) + '\n')
    
    load()
    print("[settings]")
    print("channel: " + channel)
    print("channel_key: " + channel_key.decode("utf-8"))
    print("encryption_key: " + encryption_key.decode("utf-8"))
    print("proxy: " + str(proxy))
    
def load():
    '''Load settings from settings.conf
    '''
    config = configparser.ConfigParser()
    config.read(conf_path)
    global channel
    global channel_key
    global encryption_key
    global proxy
    channel = config.get("settings", "channel")
    channel_key = config.get("settings", "channel_key")
    encryption_key = config.get("settings", "encryption_key")
    # Convert our proxy string back into a dict
    json_string = config.get("settings", "proxy").replace("'", "\"")
    proxy = json.loads(json_string)

def encrypt(plain_text):

    cipher_suite = Fernet(encryption_key)
    cipher_text = cipher_suite.encrypt(plain_text)
    return cipher_text

def decrypt(cipher_text):

    cipher_suite = Fernet(encryption_key)
    plain_text = cipher_suite.decrypt(cipher_text)
    return plain_text

def write_channel(data):
    '''Write clipboard data to channel
    '''
    response = requests.post('https://kvdb.io/' + channel + "/data", data=data, proxies=proxy, auth=(channel_key, ''))

    print("[+] Writing data to channel: " + response.url)

def read_channel():
    '''Read clipboard data from channel
    and load into clipboard
    '''
    response = requests.get('https://kvdb.io/' + channel + "/data", proxies=proxy, auth=(channel_key, ''))

    print("[+] Getting data from channel: " + response.url)

    return response.text

def copy():
    '''Read data from clipboard 
    encrypt it and write it to 
    the channel
    '''
    # Load our config (will need to do this everytime unless we run as a daemon)
    load()

    # Read the data from the clipboard
    clipboard_data = clipboard.paste()
    encrypted_clipboard = encrypt(clipboard_data.encode("utf-8"))
    
    # Write encrypted clipboard data to channel
    write_channel(encrypted_clipboard)

def paste():
    '''Read data from channel
    and copy to clipboard
    '''
    load()

    encrypted_data = read_channel()
    decrypted_data = decrypt(encrypted_data.encode("utf-8"))

    # Send data to clipboard
    clipboard.copy(decrypted_data.decode("ascii"))

parser = ArgumentParser()
parser.add_argument("-c", "--copy", dest="command", action="store_const", const="copy",
                        help="Read data from clipboard, encrypt it and then write it to the channel")

parser.add_argument("-p", "--paste", dest="command", action="store_const", const="paste",
                        help="Retrieve data from channel and copy to clipboard")

parser.add_argument("-g", "--generate", dest="command", action="store_const", const="generate", 
                        help="Generate a new channel, channel key and encryption key. Output is written to 'settings.conf'")

parser.add_argument('--conf', nargs='?', action="store", dest="conf_path", help='Optional path to write / read settings.conf file from (default is current directory)', default=os.getcwd() + "/settings.conf", required=False)

args = parser.parse_args()

global conf_path
conf_path = args.conf_path

if args.command == "copy":
    copy()

if args.command == "paste":
    paste()

if args.command == "generate":
    generate()
