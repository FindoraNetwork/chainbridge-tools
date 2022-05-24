# For Columbus Contract Deployment Toolset

## flow diagram
https://www.processon.com/diagraming/6266345563768950bc58fc32

## Usage

### InitFindora

You can use this tool to initialize Columbus Project and Prism Project. Here are two ways: 

1. If you have already prepared Prism project in Findroa chain. You can specify arguments to the `columbus` subcommand to initialize Columbus.

```
./InitFindora.py columbus --provider PROVIDER \
                        --prism-bridge PRISM_BRIDGE \
                        --prism-asset PRISM_ASSET \
                        --prism-ledger PRISM_LEDGER
```

2. You can also specify arguments to the `prism` subcommand to initialize Prism. Then run the `columbus` subcommand with default arguments to initialize Columbus.

```
./InitFindora.py prism --provider PROVIDER --prism-proxy PRISM_PROXY

./InitFindora.py columbus
```

### Add_Relayer
For adding new ChainBridge Relayer to provide performance and robustness for bridge. 

```
./Add_Relayer.py
```

**At this stage. according to the devops guide. the deployment part needs to submit PR manually.**

### Add_Network

For adding new destination networks. On it the contract deployment and setup will be done.

```
usage: Add_Network.py --name NAME --provider PROVIDER

optional arguments:
  --name NAME          New Network Name
  --provider PROVIDER  New Network Provider
```

### Sync_Relayer

Reload ChainBridge Relayer with latest Network Config.

```
./Sync_Relayer.py
```

**At this stage. according to the devops guide. the deployment part needs to submit PR manually.**

### Add_Token

* Create New wrapToken in Privacy Network
```
usage: Add_Token.py privacy burn name symbol decimal

positional arguments:
  name        The Token Name for want to create wrapToken
  symbol      wrapToken symbol
  decimal     wrapToken decimal
```

* Register Exist Token in Privacy Network
```
usage: Add_Token.py privacy lock name address

positional arguments:
  name        The Token Name for exist Token
  address     The Address of exist Token
```

* If Add wFRA, Use this SubCommand.
```
usage: Add_Token.py privacy wFRA
```

* Register Token for one Network
```
usage: Add_Token.py destination [--burn] network name address

positional arguments:
  network     Specific Network Name (Must exist in the config!!!)
  name        Specific Token Name (Must exist in the config!!!)
  address     The Address of Specific Token in Specific Network

optional arguments:
  --burn      isBurn Flag
```

### S3_Sync
Synchronize config json file for local and cloud.

* Upload
```
./S3_Sync.py upload [--bucket BUCKET] --ak AK --sk SK
```

* Download
```
./S3_Sync.py download [--website WEBSITE]
```