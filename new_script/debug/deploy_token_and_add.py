# coding=utf-8

from config import *
from util import *

from web3 import Web3
import os

# tokens = ['USDC','BUSD','DAI','WETH','WBTC','WBNB','YES']

import json
with open("/home/platform/qa04/new_script/config/deploy_config.json",'r') as f:
    qa04_config = json.load(f)

tokens = qa04_config["Token"]
w3_qa04 = Web3(Web3.HTTPProvider("https://dev-qa04.dev.findora.org:8545"))

# for t in tokens:
#     print(os.popen("./Add_Token.py 301 {0} {0} 6".format(t)).read())
#     for n in config.NetWork:
#         n_name = n['name']
#         w3 = Web3(Web3.HTTPProvider(n['Provider']))
#         token_address = Deploy_Contract(w3, t, ())
#         print("{} {} {}".format(n_name, t, token_address))
#         if n_name == 'Findora':
#             print(os.popen("./Add_Token.py 501 {} {}".format(t, token_address)).read())
#         else:
#             print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t, token_address)).read())

#         print(os.popen("./Add_Liquidity.py add {} {} 100 100 10 --amount 1000000".format(n_name, t, token_address)).read())

# for t in tokens:
#     t_name = t['name']
#     print(os.popen("./Add_Token.py 301 {0} {0} 6".format(t_name)).read())
#     for n in config.NetWork:
#         n_name = n['name']
#         w3 = Web3(Web3.HTTPProvider(n['Provider']))
#         if n_name == 'Findora':
#             token_address = Deploy_Contract(w3, t_name, ())
#             print(os.popen("./Add_Token.py 501 {} {}".format(t_name, token_address)).read())
#         else:
#             token_address = t['address'][n_name]
#             print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t_name, token_address)).read())

#         # print(os.popen("./Add_Liquidity.py add {} {} 100 100 10 --amount 1000000".format(n_name, t_name, token_address)).read())

#     input("{} Done.".format(t_name))


for t in tokens:
    t_name = t['name']

    qa04_ctoken_contract = w3_qa04.eth.contract(t["Wrap"], abi=load_abi('WrapToken'))
    decimals = qa04_ctoken_contract.functions.decimals().call()
    DECIMALS = 10 ** decimals

    minAdd = 100 * (10 ** (decimals-6))
    minFee = 60
    fixedFee = 10 * (10 ** (decimals-6))
    allocPoint = 100

    print("{}\t{}".format(t_name,decimals))

    print(os.popen("./Add_Token.py 301 {0} {0} {1}".format(t_name, decimals)).read())

   # for n in config.NetWork:
   #     n_name = n['name']
   #     if not n_name in t['address']:
   #         continue
   #     print("{}\t{}".format(n_name,t_name))

   #     if t_name == 'YES':
   #         token_address = n["columbus"]["yes"]
   #         if n_name == 'Findora':
   #             print(os.popen("./Add_Token.py 501 {} {}".format(t_name, token_address)).read())
   #         else:
   #             print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t_name, token_address)).read())

   #     else:
   #         token_address = t['address'][n_name]
   #         print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t_name, token_address)).read())

   #     w3 = Web3(Web3.HTTPProvider(n['Provider']))
   #     token_contract = w3.eth.contract(token_address, abi=load_abi('YESToken'))
   #     func = token_contract.functions.mint(load_owner().address, 1000000*2*DECIMALS)
   #     tx_hash = sign_send_wait(w3, func)
   #     print("{} {} Mint transaction hash: {}".format(n_name, t_name, tx_hash.hex()))

   #     print(os.popen("./Add_Liquidity.py add {} {} {} {} {} {} --amount 1000000".format(n_name, t_name, minAdd, minFee, fixedFee, allocPoint)).read())

    input("{} Done.".format(t_name))
        
