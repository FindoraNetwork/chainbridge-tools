# coding=utf-8

from config import *
from util import *

from debug.contract_build_deploy_test import pull_and_build
from Add_Token import Findora_w3, adminSetMinter_Relayer
from InitFindora import deployColumbusRelayer, adminSetGenericResource_Privacy

pull_and_build()

n, w3 = Findora_w3()
rc_address = deployColumbusRelayer(w3, n['handler'], n['prism']['bridge'], n['prism']['ledger'], n['columbus']['asset'], n['bridge'])
print(rc_address)

config.NetWork[0]['columbus']['relayer'] = rc_address

adminSetGenericResource_Privacy(w3, n['bridge'], n['handler'], rc_address)

for t in config.Token:
    if 'isWrap' in t:
        if t['isWrap']:
            print(t['name'])
            adminSetMinter_Relayer(t['address']['Findora'])

config.save()