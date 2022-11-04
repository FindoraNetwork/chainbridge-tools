# coding=utf-8

from config import *

import os
import json
import random

class Deploy_Config():
    def __init__(self):
        self.NetWork = []
        self.Relayer = []
        self.Token = []
        self.load()

    def load(self):
        if os.path.exists(deploy_config_path):
            with open(deploy_config_path) as f:
                config_json = json.load(f)   
                self.NetWork = config_json['NetWork']
                self.Relayer = config_json['Relayer']
                self.Token = config_json['Token']

    def save(self):
        with open(deploy_config_path,'w') as f:
            config_json = {'NetWork': self.NetWork, 'Relayer': self.Relayer, 'Token': self.Token}
            json.dump(config_json,f, indent=4)

    def checkout_name(self, i_name, i_list):
        for i in i_list:
            if i['name'] == i_name:
                return (i_list.index(i), i)

    def get_Network(self, n_name):
        return self.checkout_name(n_name, self.NetWork)

    def get_Token(self, t_name):
        # The reason is solidity mapping data structure
        # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
        t_id, t = self.checkout_name(t_name, self.Token)
        return (t_id + 1, t)

    def check_0_exist(self):
        if len(self.NetWork) == 0:
            error_print("Please Init Findora Privacy Network First!!!")
            os._exit(1)
        if self.NetWork[0]['name'] != 'Findora':
            error_print("First Network not is Findora. Config Format ERROR!!!")
            os._exit(1)

# All Script Unified config Object
config = Deploy_Config()

def load_owner():
    with open(owner_key_path, 'r') as f:
        from web3 import Web3
        owner_acct = Web3().eth.account.from_key(Web3().eth.account.decrypt(f.read(), KEYSTORE_PASSWORD))
        return owner_acct

def error_print(text):
    print("\n\033[1;31;40m{}\033[0m".format(text))

def focus_print(text):
    print("\n\033[1;36;40m{}\033[0m".format(text)) # 高亮青色前景色换行输出


def load_abi(contract_name):
    with open(contract_json_path[contract_name], 'r') as f:
        return json.load(f)['abi']

def load_functionSig(contract_name, function_name):
    with open(contract_json_path[contract_name], 'r') as f:
        hashes = json.load(f)['hashes']
    for k,v in hashes.items():
        if function_name in k:
            return v

# def sign_send_wait(w3_obj, account_obj, txn):
def sign_send_wait(w3_obj, func, value=None):
    owner_acct = load_owner()
    if value:
        txn = func.buildTransaction({'from': owner_acct.address, 'nonce': w3_obj.eth.getTransactionCount(owner_acct.address), "gasPrice": w3_obj.eth.gas_price, "value":value})
    else:
        txn = func.buildTransaction({'from': owner_acct.address, 'nonce': w3_obj.eth.getTransactionCount(owner_acct.address), "gasPrice": w3_obj.eth.gas_price})

    signed_txn = owner_acct.sign_transaction(txn)
    tx_hash = w3_obj.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3_obj.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash

def Deploy_Contract(w3_obj, contract_name, init_args):
    with open(contract_json_path[contract_name], 'r') as f:
        contract_json = json.load(f)
        abi = contract_json['abi']
        bin = contract_json['bytecode']

    contract = w3_obj.eth.contract(abi=abi, bytecode=bin)

    func = contract.constructor(*init_args)
    tx_hash = sign_send_wait(w3_obj, func)
    tx_receipt = w3_obj.eth.get_transaction_receipt(tx_hash)

    try:
        if not w3_obj.isChecksumAddress(tx_receipt.contractAddress):
            raise
    except:
        error_print("contract deployment ERROR!!!")
        print(tx_receipt)
        os._exit(1)

    return tx_receipt.contractAddress

def get_block_number(n):
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    return w3.eth.get_block_number()

def Build_Relayer_Config():
    for r in config.Relayer:
        r_id = config.Relayer.index(r)

        out_json = { "Chains":[] }
        for n in config.NetWork:
            n_id = config.NetWork.index(n)
            cur_endpoint = random.choice(n['endpoint'])
            Relayer_opts = n['Relayer_opts']
            r_blockConfirmations = (r['group']+1) * Relayer_opts['blockConfirmations'] + (r_id % 2)
            out_json['Chains'].append(
                {
                    "name": n['name'],
                    "type": "ethereum",
                    "id": str(n_id),
                    "endpoint": cur_endpoint,
                    "from": r['address'],
                    "opts": {
                        "bridge": n['bridge'],
                        # "erc20Handler": "",
                        # "erc721Handler": "",
                        "genericHandler": n['handler'],
                        "gasLimit": str(Relayer_opts['gasLimit']),
                        "maxGasPrice": str(Relayer_opts['maxGasPrice']),
                        "startBlock": str(get_block_number(n)),
                        "executeWatchLimit": str(Relayer_opts['executeWatchLimit']),
                        "blockConfirmations": str(r_blockConfirmations),
                        "http": "true"
                    }
                }
            )

        out_path = config_dir_path + "/Relayer" + "/config{}.json".format(r_id)
        with open(out_path, 'w') as f:
            json.dump(out_json,f, indent=4)


# For upgradeable
def upgradeable_Deploy(w3_obj, contract_name, init_args):
    if 'Prism' in contract_name:
        ProxyAdmin_name = 'PrismXXProxyAdmin'
        Proxy_name = 'PrismXXProxy'
    else:
        ProxyAdmin_name = 'ColumbusProxyAdmin'
        Proxy_name = 'ColumbusProxy'
    
    real_address = Deploy_Contract(w3_obj, contract_name, ())
    proxyadmin_address = Deploy_Contract(w3_obj, ProxyAdmin_name, ())

    real = w3_obj.eth.contract(real_address, abi=load_abi(contract_name))
    fun = real.encodeABI(fn_name="initialize", args=list(init_args))

    proxy_address = Deploy_Contract(w3_obj, Proxy_name, (real_address, proxyadmin_address, fun))
    return proxy_address

def upgradeable_Update(w3_obj, proxy_address, contract_name):
    if 'Prism' in contract_name:
        ProxyAdmin_name = 'PrismXXProxyAdmin'
        Proxy_name = 'PrismXXProxy'
    else:
        ProxyAdmin_name = 'ColumbusProxyAdmin'
        Proxy_name = 'ColumbusProxy'
    
    real_address = Deploy_Contract(w3_obj, contract_name, ())
    
    proxy = w3_obj.eth.contract(proxy_address, abi=load_abi(Proxy_name))
    proxyadmin_address = proxy.functions.proxyAdmin().call()
    proxyadmin = w3_obj.eth.contract(proxyadmin_address, abi=load_abi(ProxyAdmin_name))

    func = proxyadmin.functions.upgrade(proxy_address, real_address)
    tx_hash = sign_send_wait(w3_obj, func)
    print("{} ProxyAdmin.upgrade transaction hash: {}".format(contract_name, tx_hash.hex()))