# For Columbus Contract Deployment Toolset

## flow diagram
https://www.processon.com/diagraming/6266345563768950bc58fc32

## Usage

### InitFindora

* Init Findora Privacy Network

```
usage: InitFindora.py privacy --prism-bridge PRISM_BRIDGE --prism-asset
                              PRISM_ASSET
                              provider

positional arguments:
  provider              Findora Privacy Network Provider

optional arguments:
  --prism-bridge PRISM_BRIDGE
                        PrismXXBridge Contract Address
  --prism-asset PRISM_ASSET
                        PrismXXAsset Contract Address
```

* If Findora is destination chain, Use this SubCommand.
```
usage: InitFindora.py destination
```

### Add_Relayer

```
./Add_Relayer.py
```

### Add_Network

```
usage: Add_Network.py --name NAME --provider PROVIDER

optional arguments:
  --name NAME          New Network Name
  --provider PROVIDER  New Network Provider
```

### Sync_Relayer

```
./Sync_Relayer.py
```

### Add_Token

* Create New wrapToken in Privacy Network
```
usage: Add_Token.py wraptoken name symbol decimal

positional arguments:
  name        The Token Name for want to create wrapToken
  symbol      wrapToken symbol
  decimal     wrapToken decimal

```

* If Add wFRA, Use this SubCommand.
```
usage: Add_Token.py wFRA
```

* manual input Token Address for one Network
```
usage: Add_Token.py token [--burn] network name address

positional arguments:
  network     Specific Network Name (Must exist in the config!!!)
  name        Specific Token Name (Must exist in the config!!!)
  address     The Address of Specific Token in Specific Network

optional arguments:
  --burn      isBurn Flag
```