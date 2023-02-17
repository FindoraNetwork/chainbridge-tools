#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

from Add_Liquidity import Farm_add, deployCTokenContract

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser.add_argument('allocPoint', help="How many allocation points assigned to this pool. YESs to distribute per block. MaxAllocPoint = 4000.")
    args = parser.parse_args()

    config.check_0_exist()

    _, n = config.get_Network(args.network)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    _, t = config.get_Token(args.name)
    token_address = t['address'][args.network]

    focus_print("Deployment AssetCertificate Contract")
    AssetCert_address = Deploy_Contract(w3, "AssetCertificate", ("AC"+args.name, "AC"+args.name))
    focus_print("Deployment ColumbusStaking Contract")
    staking_address = Deploy_Contract(w3, "ColumbusStaking", ())

    farm_address = n["columbus"]["farm"]
    farm_contract = w3.eth.contract(farm_address, abi=load_abi("TreasureCave"))
    columbusFarmPid = farm_contract.functions.poolLength().call()

    focus_print("Call Staking.initialize")
    staking_contract = w3.eth.contract(staking_address, abi=load_abi('ColumbusStaking'))
    _vault = '0x0000000000000000000000000000000000000000'
    _treasury = '0x0000000000000000000000000000000000000000'
    func = staking_contract.functions.initialize(
        token_address,
        n["columbus"]["yes"],
        farm_address,
        AssetCert_address,
        _vault,
        _treasury,
        columbusFarmPid
    )
    tx_hash = sign_send_wait(w3, func)
    print("Staking.initialize transaction hash: {}".format(tx_hash.hex()))

    focus_print("AssetCertificate.setMinter To Staking")
    AssetCert_contract = w3.eth.contract(AssetCert_address, abi=load_abi("AssetCertificate"))
    func = AssetCert_contract.functions.setMinter(staking_address)
    tx_hash = sign_send_wait(w3, func)
    print("setMinter {} transaction hash: {}".format(staking_address, tx_hash.hex()))

    focus_print("Deployment dummyToken Contract")
    dummyToken_address = deployCTokenContract(w3, token_address)

    focus_print("Farm_add new lpToken")
    farm_address = n["columbus"]["farm"]
    lpToken_address = dummyToken_address
    Farm_add(w3, farm_address, args.allocPoint, lpToken_address)

    focus_print("Mint dummyToken and Approve To Staking")
    dummyToken_contract = w3.eth.contract(dummyToken_address, abi=load_abi("CToken"))
    decimals = dummyToken_contract.functions.decimals().call()
    DECIMALS = 10 ** decimals
    func = dummyToken_contract.functions.mint(load_owner().address, 8000000*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("Mint transaction hash: {}".format(tx_hash.hex()))
    func = dummyToken_contract.functions.approve(staking_address, 8000000*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("Approve transaction hash: {}".format(tx_hash.hex()))

    focus_print("Farm grantRole POOL_ROLE")
    POOL_ROLE = farm_contract.functions.POOL_ROLE().call()
    func = farm_contract.functions.grantRole(POOL_ROLE, staking_address)
    tx_hash = sign_send_wait(w3, func)
    print("Farm POOL_ROLE transaction hash: {}".format(tx_hash.hex()))

    focus_print("Call Staking.init")
    func = staking_contract.functions.init(dummyToken_address)
    tx_hash = sign_send_wait(w3, func)
    print("Staking.init transaction hash: {}".format(tx_hash.hex()))

    focus_print("Call Staking.setColumbus to Deck")
    deck_address = n["columbus"]["deck"]
    func = staking_contract.functions.setColumbus(deck_address)
    tx_hash = sign_send_wait(w3, func)
    print("Staking.setColumbus {} transaction hash: {}".format(deck_address, tx_hash.hex()))

    print("AssetCertificate Address:\t"+AssetCert_address)
    print("ColumbusStaking Address:\t"+staking_address)
    print("dummyToken Address:\t"+dummyToken_address)

    focus_print("Call Deck.setContractWhitelist to Staking")
    deck_contract = w3.eth.contract(deck_address, abi=load_abi("ColumbusDeck"))
    func = deck_contract.functions.setContractWhitelist(staking_address)
    tx_hash = sign_send_wait(w3, func)
    print("Deck.setContractWhitelist {} transaction hash: {}".format(staking_address, tx_hash.hex()))

    focus_print("Call Deck.setDepositFunctionSignature")
    depositSig = load_functionSig("ColumbusStaking","depositFromColumbus")
    _gas = 0
    func = deck_contract.functions.setDepositFunctionSignature(
        staking_address,
        depositSig,
        _gas
    )
    tx_hash = sign_send_wait(w3, func)
    print("Deck.setDepositFunctionSignature transaction hash: {}".format(tx_hash.hex()))
