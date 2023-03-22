# coding=utf-8

from web3 import Web3
import solcx
import json
import os

def pull_and_build():
    print(os.popen('su - ys -c "cd ~/ys-contracts && git pull"').read())

    # os.chdir("/home/platform/chainbridge-solidity/node_modules/@openzeppelin/contracts")

    # compiled = solcx.compile_files(
    #     ["token/ERC20/ERC20.sol"],
    #     output_values=['abi'],
    #     solc_version="0.6.4",
    #     allow_paths=["/home/platform/chainbridge-solidity/node_modules/@openzeppelin/contracts"]
    # )['token/ERC20/ERC20.sol:ERC20']

    # print(compiled.keys())

    # with open("/home/platform/chainbridge-tools/new_script/contracts/ERC20.json", 'w') as f:
    #     json.dump(compiled,f, indent=4)

    pwd = os.getcwd()
    os.chdir("/home/ys/ys-contracts/contracts")

    os.system("cp -f staking/* .")
    os.system('''sed -i 's#"contracts/#"./#g' *.sol''')

    disable_list = [
        "Greeter.sol",
        "ColumbusMath.sol",
        "Pay.sol"
    ]

    sol_files = []
    for i in os.listdir("."):
        if ".sol" in i and i not in disable_list:
            sol_files.append(i)

    compiled = solcx.compile_files(
        sol_files,
        output_values=['abi', 'bin', 'hashes'],
        solc_version="0.8.17",
        allow_paths=["/home/ys/ys-contracts/contracts"],
        optimize=True
    )

    # key_list = ['{}:{}'.format(i, i.split(".sol")[0]) for i in sol_files ]
    key_list = []
    for i in sol_files:
        if i == "wToken.sol":
            key_list.append("wToken.sol:WrapToken")
            continue
        if i == "cToken.sol":
            key_list.append("cToken.sol:CToken")
            continue
        if i == "ColumbusFarm.sol":
            key_list.append("ColumbusFarm.sol:TreasureCave")
            continue
        if i == "ColumbusToken.sol":
            key_list.append("ColumbusToken.sol:YESToken")
            continue
        key_list.append('{}:{}'.format(i, i.split(".sol")[0]))

    os.chdir(pwd)    

    for i in key_list:
        compiled_item = compiled[i]
        compiled_item['bytecode'] = "0x" + compiled_item['bin']
        del(compiled_item['bin'])

        with open("contracts/{}.json".format(i.split(':')[1]), 'w') as f:
            json.dump(compiled_item,f, indent=4)


if __name__ == '__main__':
    pull_and_build()
# ============================================================================

# w3 = Web3(Web3.HTTPProvider("http://172.20.0.202:8545"))
# w3 = Web3(Web3.HTTPProvider("http://172.20.0.201:8545"))
# print(w3.eth.accounts)

# print(w3.eth.get_balance(w3.eth.accounts[0]))

# with open("/home/platform/chainbridge-tools/new_script/keys/owner_keystore.json", 'r') as f:
#     owner_acct = Web3().eth.account.from_key(Web3().eth.account.decrypt(f.read(), "passw0rd"))

# tx_hash = w3.eth.send_transaction({
#    'from': w3.eth.accounts[0],
#    'to': owner_acct.address,
#    'value': w3.toWei(10, 'ether')
# })
# w3.eth.wait_for_transaction_receipt(tx_hash)

# print(w3.eth.get_balance(w3.eth.accounts[0]))
# print(w3.eth.get_balance(owner_acct.address))


# with open("/home/platform/chainbridge-tools/new_script/contracts/test_out.json") as f:
#     contract_json = json.load(f)
#     bridge_abi = contract_json['abi']
#     bridge_bin = contract_json['bytecode']

# bridge_contract = w3.eth.contract(abi=bridge_abi, bytecode=bridge_bin)

# # tx_hash = bridge_contract.constructor(0, ["0x1962C55A61a4B7A8941C6dfcefE2FeD176f99cda"], 1, 0, 100).transact()
# txn= bridge_contract.constructor(0, [], 1, 0, 100).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
# signed_txn = owner_acct.sign_transaction(txn)
# tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# print(tx_receipt.contractAddress)
# print(w3.eth.get_balance(owner_acct.address))

# bridge_contract = w3.eth.contract(Web3.toChecksumAddress("0x17A97707f8f817eCb59D05177ec4B114d3aeE187"), abi=bridge_abi)
# print(bridge_contract.functions._chainID().call())
