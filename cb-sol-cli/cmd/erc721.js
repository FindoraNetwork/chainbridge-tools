const ethers = require('ethers');
const constants = require('../constants');

const {Command} = require('commander');
const {setupParentArgs, waitForTx, log} = require("./utils")

const isAdminCmd = new Command("is-admin")
    .description("Check if address is admin")
    .option('--admin <value>', 'Address to check', constants.deployerAddress)
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        let res = await erc721Instance.hasRole(constants.ADMIN_ROLE, args.admin)
        console.log(`[${args._name}] Address ${args.admin} ${res ? "is" : "is not"} an admin.`)
    })

const addAdminCmd = new Command("add-admin")
    .description("Add an admin")
    .option('--admin <address>', 'Address of admin', constants.adminAddresses[0])
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        log(args, `Adding ${args.admin} as an admin.`)
        let tx = await erc721Instance.grantRole(constants.ADMIN_ROLE, args.admin)
        await waitForTx(args.provider, tx.hash)
    })

const renounceAdminCmd = new Command("renounce-admin")
    .description("Renounce an admin")
    .option('--admin <address>', 'Address of current admin', constants.adminAddresses[0])
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        log(args, `Renouncing ${args.admin} as an admin.`)
        let tx = await erc721Instance.renounceRole(constants.ADMIN_ROLE, args.admin)
        await waitForTx(args.provider, tx.hash)
    })

const mintCmd = new Command("mint")
    .description("Mint tokens")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--id <id>', "Token id", "0x1")
    .option('--metadata <bytes>', "Metadata (tokenURI) for token", "")
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);

        log(args, `Minting token with id ${args.id} to ${args.wallet.address} on contract ${args.erc721Address}!`);
        const tx = await erc721Instance.mint(args.wallet.address, ethers.utils.hexlify(args.id), args.metadata);
        await waitForTx(args.provider, tx.hash)
    })

const ownerCmd = new Command("owner")
    .description("Query ownerOf")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--id <id>', "Token id", "0x1")
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        const owner = await erc721Instance.ownerOf(ethers.utils.hexlify(args.id))
        log(args, `Owner of token ${args.id} is ${owner}`)
    })

const isMinterCmd = new Command("is-minter")
    .description("Check if address is minter")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--minter <value>', 'Address to check', constants.relayerAddresses[0])
    .action(async function (args) {
            await setupParentArgs(args, args.parent.parent)
            const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
            let MINTER_ROLE = await erc721Instance.MINTER_ROLE();
            let res = await erc721Instance.hasRole(MINTER_ROLE, args.minter)
            console.log(`[${args._name}] Address ${args.minter} ${res ? "is" : "is not"} a minter.`)
    })

const addMinterCmd = new Command("add-minter")
    .description("Add a new minter to the contract")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--minter <address>', 'Minter address', constants.relayerAddresses[1])
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        const MINTER_ROLE = await erc721Instance.MINTER_ROLE()
        log(args, `Adding ${args.minter} as a minter of ${args.erc721Address}`)
        const tx = await erc721Instance.grantRole(MINTER_ROLE, args.minter);
        await waitForTx(args.provider, tx.hash)
    })

    const removeMinterCmd = new Command("remove-minter")
    .description("Remove a minter from the contract")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--minter <address>', 'Minter address', constants.relayerAddresses[1])
    .action(async function(args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        let MINTER_ROLE = await erc721Instance.MINTER_ROLE();
        log(args, `Removing ${args.minter} as a minter on contract ${args.erc721Address}`);
        const tx = await erc721Instance.revokeRole(MINTER_ROLE, args.minter);
        await waitForTx(args.provider, tx.hash)
    })

const isPauserCmd = new Command("is-pauser")
    .description("Check if address is pauser")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--pauser <value>', 'Address to check', constants.relayerAddresses[0])
    .action(async function (args) {
            await setupParentArgs(args, args.parent.parent)
            const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
            let PAUSER_ROLE = await erc721Instance.PAUSER_ROLE();
            let res = await erc721Instance.hasRole(PAUSER_ROLE, args.pauser)
            console.log(`[${args._name}] Address ${args.pauser} ${res ? "is" : "is not"} a pauser.`)
    })

const addPauserCmd = new Command("add-pauser")
    .description("Add a new pauser to the contract")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--pauser <address>', 'Pauser address', constants.relayerAddresses[1])
    .action(async function(args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        let PAUSER_ROLE = await erc721Instance.PAUSER_ROLE();
        log(args, `Adding ${args.pauser} as a pauser on contract ${args.erc721Address}`);
        const tx = await erc721Instance.grantRole(PAUSER_ROLE, args.pauser);
        await waitForTx(args.provider, tx.hash)
    })

const removePauserCmd = new Command("remove-pauser")
    .description("Remove a pauser from the contract")
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .option('--pauser <address>', 'Pauser address', constants.relayerAddresses[1])
    .action(async function(args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);
        let PAUSER_ROLE = await erc721Instance.PAUSER_ROLE();
        log(args, `Removing ${args.pauser} as a pauser on contract ${args.erc721Address}`);
        const tx = await erc721Instance.revokeRole(PAUSER_ROLE, args.pauser);
        await waitForTx(args.provider, tx.hash)
    })

const approveCmd = new Command("approve")
    .description("Approve tokens for transfer")
    .option('--id <id>', "Token ID to transfer", "0x1")
    .option('--recipient <address>', 'Destination recipient address', constants.ERC721_HANDLER_ADDRESS)
    .option('--erc721Address <address>', 'ERC721 contract address', constants.ERC721_ADDRESS)
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)
        const erc721Instance = new ethers.Contract(args.erc721Address, constants.ContractABIs.Erc721Mintable.abi, args.wallet);

        log(args, `Approving ${args.recipient} to spend token ${args.id} from ${args.wallet.address} on contract ${args.erc721Address}!`);
        const tx = await erc721Instance.approve(args.recipient, ethers.utils.hexlify(args.id), {
            gasPrice: args.gasPrice,
            gasLimit: args.gasLimit
        });
        await waitForTx(args.provider, tx.hash)
    })

const depositCmd = new Command("deposit")
    .description("Initiates a bridge transfer")
    .option('--id <id>', "ERC721 token id", "0x1")
    .option('--dest <value>', "destination chain", "1")
    .option(`--recipient <address>`, 'Destination recipient address', constants.relayerAddresses[4])
    .option('--resourceId <resourceID>', 'Resource ID for transfer', constants.ERC721_RESOURCEID)
    .option('--bridge <address>', 'Bridge contract address', constants.BRIDGE_ADDRESS)
    .action(async function (args) {
        await setupParentArgs(args, args.parent.parent)

        // Instances
        const bridgeInstance = new ethers.Contract(args.bridge, constants.ContractABIs.Bridge.abi, args.wallet);

        const data = '0x' +
            ethers.utils.hexZeroPad(ethers.utils.hexlify(args.id), 32).substr(2) +  // Deposit Amount        (32 bytes)
            ethers.utils.hexZeroPad(ethers.utils.hexlify((args.recipient.length - 2) / 2), 32).substr(2) +       // len(recipientAddress) (32 bytes)
            ethers.utils.hexlify(args.recipient).substr(2)                // recipientAddress      (?? bytes)

        log(args, `Constructed deposit:`)
        log(args, `  Resource Id: ${args.resourceId}`)
        log(args, `  Token Id: ${args.id}`)
        log(args, `  len(recipient): ${(args.recipient.length - 2) / 2}`)
        log(args, `  Recipient: ${args.recipient}`)
        log(args, `  Raw: ${data}`)
        log(args, "Creating deposit to initiate transfer!")

        // Perform deposit
        const tx = await bridgeInstance.deposit(
            args.dest, // destination chain id
            args.resourceId,
            data,
            {gasPrice: args.gasPrice, gasLimit: args.gasLimit});
        await waitForTx(args.provider, tx.hash)
    })

const createErc721ProposalData = (id, recipient, metadata) => {
    if (recipient.substr(0, 2) === "0x") {
        recipient = recipient.substr(2)
    }
    if (metadata.substr(0, 2) === "0x") {
        metadata = metadata.substr(2)
    }
    console.log(metadata)
    return '0x' +
        ethers.utils.hexZeroPad(ethers.utils.bigNumberify(id).toHexString(), 32).substr(2) +
        ethers.utils.hexZeroPad(ethers.utils.hexlify(recipient.length / 2 + recipient.length % 2), 32).substr(2) +
        recipient +
        ethers.utils.hexZeroPad(ethers.utils.hexlify(metadata.length / 2 + metadata.length % 2), 32).substr(2) +
        metadata;
}

const proposalDataHashCmd = new Command("data-hash")
    .description("Hash the proposal data for an erc721 proposal")
    .option('--id <value>', "Token ID", 1)
    .option('--recipient <address>', 'Destination recipient address', constants.relayerAddresses[4])
    .option('--metadata <metadata>', 'Token metadata', "")
    .option('--handler <address>', 'ERC721 handler address', constants.ERC20_HANDLER_ADDRESS)
    .action(async function (args) {
        console.log(args.metadata)
        const data = createErc721ProposalData(args.id, args.recipient, args.metadata)
        const hash = ethers.utils.solidityKeccak256(["address", "bytes"], [args.handler, data])

        log(args, `Hash: ${hash} Data: ${data}`)
    })

const erc721Cmd = new Command("erc721")

erc721Cmd.addCommand(isAdminCmd)
erc721Cmd.addCommand(addAdminCmd)
erc721Cmd.addCommand(renounceAdminCmd)
erc721Cmd.addCommand(mintCmd)
erc721Cmd.addCommand(ownerCmd)
erc721Cmd.addCommand(isMinterCmd)
erc721Cmd.addCommand(addMinterCmd)
erc721Cmd.addCommand(removeMinterCmd)
erc721Cmd.addCommand(isPauserCmd)
erc721Cmd.addCommand(addPauserCmd)
erc721Cmd.addCommand(removePauserCmd)
erc721Cmd.addCommand(approveCmd)
erc721Cmd.addCommand(depositCmd)
erc721Cmd.addCommand(proposalDataHashCmd)

module.exports = erc721Cmd
