# coding=utf-8

import os

config_dir_path = os.getcwd() + "/config"
if not os.path.exists(config_dir_path):
    os.mkdir(config_dir_path)
key_dir_path = os.getcwd() + "/keys"
if not os.path.exists(key_dir_path):
    os.mkdir(key_dir_path)

deploy_config_path = config_dir_path + "/deploy_config.json"
owner_key_path = key_dir_path + "/owner_keystore.json"
password_path = key_dir_path + "/KEYSTORE_PASSWORD"
chainbridge_bin_path = "/home/platform/chainbridge/build/chainbridge"

gasLimit = 1000000
maxGasPrice = 100000000000
executeWatchLimit = 225
blockConfirmations = 3

with open(password_path, 'r') as f:
    KEYSTORE_PASSWORD = f.read()

# uni_resourceID = "0x000000000000000000000000000000c76ebe4a02bbc34786d860b355f5111301"
resourceID_301 = "0x000000000000000000000000000000c76ebe4a02bbc34786d860b355f5111301"
resourceID_501 = "0x000000000000000000000000000000c76ebe4a02bbc34786d860b355f5111501"

mnemonic_file_path = "/home/platform/findora_wallet/Mnemonic_Big_qa02"

contract_json_path = {}
for i in os.listdir('contracts'):
    contract_json_path[i[:-5]] = 'contracts/'+i