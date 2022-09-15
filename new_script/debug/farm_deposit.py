# coding=utf-8

from web3 import Web3

from config import *
from util import *

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('network')
parser.add_argument('amount')
args = parser.parse_args()

_, n = config.get_Network(args.network)
w3 = Web3(Web3.HTTPProvider(n['Provider']))

Farm_address = n['columbus']['farm']
Farm_contract = w3.eth.contract(Farm_address, abi=load_abi('ColumbusFarm'))

for t in config.Token:
    if t['name'] == "YES":
        continue

    erc20_abi = load_abi("ERC20")
    cToken_address = t['cToken'][n['name']]
    cToken_contract = w3.eth.contract(cToken_address, abi=erc20_abi)
    decimals = cToken_contract.functions.decimals().call()
    DECIMALS = 10 ** decimals

    func = cToken_contract.functions.approve(Farm_address, int(args.amount)*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("Approve transaction hash: {}".format(tx_hash.hex()))

    _pid = config.Token.index(t)
    func = Farm_contract.functions.deposit(_pid, int(args.amount)*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("LP_addLiquidity {} transaction hash: {}".format(cToken_address, tx_hash.hex()))