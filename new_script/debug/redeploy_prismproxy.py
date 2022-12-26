# coding=utf-8

from config import *
from util import *

from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://dev-qa02.dev.findora.org:8545"))
proxy_address = Deploy_Contract(w3, "PrismProxy", ())
print("PrismProxy\t{}".format(proxy_address))