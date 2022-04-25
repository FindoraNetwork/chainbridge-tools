# coding=utf-8

from web3 import Web3
import json
import os
import sys

config_dir_path = os.getcwd() + "/config"
if not os.path.exists(config_dir_path):
    os.mkdir(config_dir_path)
key_dir_path = os.getcwd() + "/keys"
if not os.path.exists(key_dir_path):
    os.mkdir(key_dir_path)

deploy_config_path = config_dir_path + "/deploy_config.json"
owner_key_path = key_dir_path + "/owner_keystore.json"

KEYSTORE_PASSWORD = "passw0rd"

def load_config():
    global config
    if os.path.exists(deploy_config_path):
        with open(deploy_config_path) as f:
            config = json.load(f)
    else:
        config = { "NetWork": [], "Relayer": [], "Token": [] }

def save_config():
    with open(deploy_config_path,'w') as f:
        json.dump(config,f, indent=4)

def focus_print(text):
    print("\n\033[1;36;40m{}\033[0m".format(text)) # 高亮青色前景色换行输出

def sign_send_wait(w3_obj, account_obj, txn):
    signed_txn = account_obj.sign_transaction(txn)
    tx_hash = w3_obj.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3_obj.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash


with open(owner_key_path, 'r') as f:
    owner_acct = Web3().eth.account.from_key(Web3().eth.account.decrypt(f.read(), KEYSTORE_PASSWORD))

Network_Name = sys.argv[1]
Network_Provider = sys.argv[2]
w3 = Web3(Web3.HTTPProvider(Network_Provider))

def deployBridgeContract(chainID):
    with open("contracts/Bridge.json") as f:
        contract_json = json.load(f)
        bridge_abi = contract_json['abi']
        bridge_bin = contract_json['bytecode']

    bridge_contract = w3.eth.contract(abi=bridge_abi, bytecode=bridge_bin)

    txn= bridge_contract.constructor(chainID, [], 1, 0, 100).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
    tx_hash = sign_send_wait(w3, owner_acct, txn)
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

def deployGenericHandler(bridge_address):
    with open("contracts/GenericHandler.json") as f:
        contract_json = json.load(f)
        handler_abi = contract_json['abi']
        handler_bin = contract_json['bytecode']

    handler_contract = w3.eth.contract(abi=handler_abi, bytecode=handler_bin)

    txn= handler_contract.constructor(bridge_address, [], [], [], []).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
    tx_hash = sign_send_wait(w3, owner_acct, txn)
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

def deployColumbusDeck(genericHandlerAddress):
    with open("contracts/ColumDeck.json") as f:
        contract_json = json.load(f)
        deck_abi = contract_json['abi']
        deck_bin = contract_json['bytecode']

    deck_contract = w3.eth.contract(abi=deck_abi, bytecode=deck_bin)

    txn= deck_contract.constructor(genericHandlerAddress).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
    tx_hash = sign_send_wait(w3, owner_acct, txn)
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

def adminAddRelayer(bridge_address):
    with open("contracts/Bridge.json") as f:
        bridge_abi = json.load(f)['abi']

    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    for r in config['Relayer']:
        txn = bridge_contract.functions.adminAddRelayer(r['address']).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
        tx_hash = sign_send_wait(w3, owner_acct, txn)
        print("{} adminAddRelayer transaction hash: {}".format(r['name'], tx_hash.hex()))

load_config()

focus_print("Deployment Bridge Contract")
bridge_address = deployBridgeContract(len(config['NetWork']))

focus_print("Deployment GenericHandler Contract")
handler_address = deployGenericHandler(bridge_address)

focus_print("Deployment ColumbusDeck Contract")
deck_address = deployColumbusDeck(handler_address)

focus_print("adminAddRelayer for Existing Relayer")
adminAddRelayer(bridge_address)

config['NetWork'].append(
    {
        "name": Network_Name,
        "Provider": Network_Provider,
        "endpoint": [
            Network_Provider
        ],
        "bridge": bridge_address,
        "handler": handler_address,
        "deck": deck_address
    }
)

save_config()