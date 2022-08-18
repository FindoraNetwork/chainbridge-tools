# coding=utf-8

from config import *
from util import *

from web3 import Web3
import os

import json
with open("/home/platform/chainbridge-tools/new_script/config/deploy_config.json",'r') as f:
    qa02_config = json.load(f)
tokens = qa02_config["Token"]


for n in config.NetWork[1:]:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    asset_contract = w3.eth.contract(n['columbus']['asset'], abi=load_abi("ColumbusAsset"))
    
    n_name = n['name']
    print(n_name)
    for t in tokens:
        i = tokens.index(t) + 1
        t_name, token_address = t['name'], t['address'][n_name]

        cur_address = asset_contract.functions.getTokenAddressByTokenId(i).call()
        if cur_address == token_address:
            continue

        print("{}\t{}\t{}".format(t_name, cur_address, token_address))
        print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t_name, token_address)).read())
        print(os.popen("./Add_Liquidity.py add {} {} 100 60 10 --amount 1000000".format(n_name, t_name)).read()) # 不管decimal先暂时100 60 10 后面再改
