# coding=utf-8

from config import *
from util import *

from web3 import Web3

for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    # if n['name'] == 'Findora':
    #     LP_address = n['columbus']["chain501"]['pool']
    # else:
    #     LP_address = n['columbus']['pool']
    # upgradeable_Update(w3, LP_address, "ColumbusPool")

    # Relayer && Deck upgrade
    if n['name'] == 'Findora':
        upgradeable_Update(w3, n['columbus']["chain301"]['relayer'], "ColumbusRelayer")
        upgradeable_Update(w3, n['columbus']["chain501"]['relayer'], "ColumbusRelayer")

    # else:
    #     upgradeable_Update(w3, n['columbus']['deck'], "ColumbusDeck")

# # SimBridge upgrade
# n0 = config.NetWork[0]
# w3 = Web3(Web3.HTTPProvider(n0['Provider']))
# upgradeable_Update(w3, n0['columbus']["chain501"]['simbridge'], "ColumbusSimBridge")