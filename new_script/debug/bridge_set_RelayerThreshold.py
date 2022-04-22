# coding=utf-8

from web3 import Web3
import json

Findora_Provider = "https://dev-qa03.dev.findora.org:8545/"

w3_Findora = Web3(Web3.HTTPProvider(Findora_Provider))

bridge_address_Findora_BSC = "0x955edabDD37C8aFC398dFC11870cb05AaEf39e04"
bridge_address_Findora_ETH = "0x9b02A1A54f940eA4D7cBad24B1b053eb3ef5Ce32"
with open("../contracts/Bridge.json") as f:
    bridge_abi = json.load(f)['abi']
bridge_contract_Findora_BSC = w3_Findora.eth.contract(bridge_address_Findora_BSC, abi=bridge_abi)
bridge_contract_Findora_ETH = w3_Findora.eth.contract(bridge_address_Findora_ETH, abi=bridge_abi)

brige_BSC_admin_account = w3_Findora.eth.account.from_key("0xe1ef1f9764dd5513ab7d255fb98dfdc1feb2905cc1065ce9cce6ece61d6804f8")
brige_ETH_admin_account = w3_Findora.eth.account.from_key("0x11be28904502afcec574b2616d502c5156198a6d214f23e4d4adb23f8ca23a22")


def set_RelayerThreshold(bridge_contract_Findora, admin_account):
    print("{} _relayerThreshold: {}".format(bridge_contract_Findora.address, bridge_contract_Findora.functions._relayerThreshold().call()))

    txn = bridge_contract_Findora.functions.adminChangeRelayerThreshold(1).buildTransaction({'from': admin_account.address, 'nonce': w3_Findora.eth.getTransactionCount(admin_account.address), "gasPrice": w3_Findora.eth.gas_price})
    signed_txn = admin_account.sign_transaction(txn)
    tx_hash = w3_Findora.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3_Findora.eth.wait_for_transaction_receipt(tx_hash)
    tx_receipt = w3_Findora.eth.get_transaction_receipt(tx_hash)
    print(tx_receipt)

    print("{} _relayerThreshold: {}".format(bridge_contract_Findora.address, bridge_contract_Findora.functions._relayerThreshold().call()))

set_RelayerThreshold(bridge_contract_Findora_BSC, brige_BSC_admin_account)
set_RelayerThreshold(bridge_contract_Findora_ETH, brige_ETH_admin_account)