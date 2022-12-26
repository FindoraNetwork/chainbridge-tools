# coding=utf-8

from config import *
from util import *

from web3 import Web3

n = config.NetWork[0]
w3 = Web3(Web3.HTTPProvider(n['Provider']))

func_list = []

relayer_301 = w3.eth.contract(n['columbus']['chain301']['relayer'], abi=load_abi("ColumbusRelayer"))
func_list.append(relayer_301.functions.adminSetPrismAddress(n['prism']['bridge']))
func_list.append(relayer_301.functions.adminSetPrismLedgerAddress(n['prism']['ledger']))

relayer_501 = w3.eth.contract(n['columbus']['chain501']['relayer'], abi=load_abi("ColumbusRelayer"))
func_list.append(relayer_501.functions.adminSetPrismAddress(n['prism']['bridge']))
func_list.append(relayer_501.functions.adminSetPrismLedgerAddress(n['prism']['ledger']))

simbridge_501 = w3.eth.contract(n['columbus']['chain501']['simbridge'], abi=load_abi("ColumbusSimBridge"))
func_list.append(simbridge_501.functions.adminSetPrismBridgeAddress(n['prism']['bridge'], n['prism']['ledger']))

for t in config.Token:
    wrap_contract = w3.eth.contract(t["Wrap"], abi=load_abi('WrapToken'))
    func_list.append(wrap_contract.functions.adminSetMinter(n["prism"]["ledger"]))

for func in func_list:
    print(sign_send_wait(w3, func).hex())
