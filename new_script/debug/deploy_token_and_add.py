# coding=utf-8

from config import *
from util import *

from web3 import Web3
import os

# tokens = ['USDC','BUSD','DAI','WETH','WBTC','WBNB','YES']

import json
with open("/home/platform/chainbridge-tools/new_script/config/deploy_config.json",'r') as f:
    qa02_config = json.load(f)

tokens = qa02_config["Token"][1:]

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

for t in tokens:
    t_name = t['name']
    print(os.popen("./Add_Token.py 301 {0} {0} 6".format(t_name)).read())
    for n in config.NetWork:
        n_name = n['name']
        w3 = Web3(Web3.HTTPProvider(n['Provider']))
        if n_name == 'Findora':
            token_address = Deploy_Contract(w3, t_name, ())
            print(os.popen("./Add_Token.py 501 {} {}".format(t_name, token_address)).read())
        else:
            token_address = t['address'][n_name]
            print(os.popen("./Add_Token.py destination {} {} {}".format(n_name, t_name, token_address)).read())

        # print(os.popen("./Add_Liquidity.py add {} {} 100 100 10 --amount 1000000".format(n_name, t_name, token_address)).read())

    input("{} Done.".format(t_name))
        