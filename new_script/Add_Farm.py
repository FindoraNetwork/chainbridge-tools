#!/usr/bin/env python3
# coding=utf-8

import os
from web3 import Web3

from config import *
from util import *

def deployColumbusFarm(w3, _yes, _yesPerSecond, _startTime, _endTime):
    return Deploy_Contract(w3, "ColumbusFarm", (_yes, int(_yesPerSecond), int(_startTime), int(_endTime)))

def YES_transferOwnership(w3, yes_address, farm_address):
    YES_contract = w3.eth.contract(yes_address, abi=load_abi("ColumbusToken"))
    func = YES_contract.functions.transferOwnership(farm_address)
    tx_hash = sign_send_wait(w3, func)
    print("YES_transferOwnership transaction hash: {}".format(tx_hash.hex()))

def Farm_add(w3, farm_address, _allocPoint, _lpToken):
    farm_contract = w3.eth.contract(farm_address, abi=load_abi("ColumbusFarm"))
    func = farm_contract.functions.add(int(_allocPoint), _lpToken)
    tx_hash = sign_send_wait(w3, func)
    print("Farm_add transaction hash: {}".format(tx_hash.hex()))


def func_deploy(args):
    _, n = config.get_Network(args.network)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    try:
        _, t = config.get_Token('YES')
        yes_address = t['address'][n['name']]
    except:
        error_print("YES Token is not deployed in the specified network.")
        os._exit(1)

    focus_print("Deployment ColumbusFarm Contract")
    farm_address = deployColumbusFarm(w3, yes_address, args.yesPerSecond, args.startTime, args.endTime)
    focus_print("YES.transferOwnership To Farm")
    YES_transferOwnership(w3, yes_address, farm_address)

    n["columbus"]["farm"] = farm_address

    config.save()

def func_add(args):
    if args.token == 'YES':
        error_print("Forbid infinite loop!!!")
        os._exit(1)

    _, n = config.get_Network(args.network)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    farm_address = n["columbus"]["farm"]
    _, t = config.get_Token(args.token)
    lpToken_address = t['cToken'][args.network]

    focus_print("Farm_add new lpToken")
    Farm_add(w3, farm_address, args.allocPoint, lpToken_address)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Add Farm for one Network")
    subparsers = parser.add_subparsers(dest='Add_Farm SubCommand')
    subparsers.required = True

    parser_deploy = subparsers.add_parser('deploy', help='Deployment Farm Contracts')
    parser_deploy.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_deploy.add_argument('yesPerSecond', help="YES tokens created per second. Unit wei.")
    parser_deploy.add_argument('startTime', help="The block time when YES mining starts. Unix timestamp.")
    parser_deploy.add_argument('endTime', help="The block time when YES mining stops. Unix timestamp.")
    parser_deploy.set_defaults(func=func_deploy)

    parser_add = subparsers.add_parser('add', help='Add a new lp to the pool.')
    parser_add.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_add.add_argument('token', help="Specific Token Name (Must exist in the config!!!)")
    parser_add.add_argument('allocPoint', help="How many allocation points assigned to this pool. YESs to distribute per block.")
    parser_add.set_defaults(func=func_add)

    args = parser.parse_args()
    args.func(args)