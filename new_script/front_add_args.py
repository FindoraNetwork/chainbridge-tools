#!/usr/bin/env python3
# coding=utf-8

from util import config

import argparse
parser = argparse.ArgumentParser(description="This tool can insert additional parameters used by the frontend into the configuration file.")
parser.add_argument('network')
parser.add_argument('--ws', help="WebSocket Provider")
parser.add_argument('--explorer', help="Block Explorer")
parser.add_argument('--chainid', help="EVM ChainId https://chainlist.org")
args = parser.parse_args()

n_id, n = config.get_Network(args.network)
if not "Frontend" in config.NetWork[n_id]:
    config.NetWork[n_id]["Frontend"] = {}

if args.ws:
    config.NetWork[n_id]["Frontend"]["Provider_WS"] = args.ws

if args.explorer:
    config.NetWork[n_id]["Frontend"]["Explorer"] = args.explorer

if args.chainid:
    config.NetWork[n_id]["Frontend"]["ChainId"] = args.chainid


config.save()