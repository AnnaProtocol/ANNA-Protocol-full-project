const { ethers } = require("ethers");
require("dotenv").config();

async function main() {
    const provider = new ethers.JsonRpcProvider(process.env.POLYGON_AMOY_RPC);
    const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
    
    const balance = await provider.getBalance(wallet.address);
    const balanceInMatic = ethers.formatEther(balance);
    const network = await provider.getNetwork();
    console.log("🌐 Network:", network.name);
    console.log("🆔 Chain ID:", network.chainId);
    console.log("\n💰 Saldo da Carteira\n");
    console.log("Address:", wallet.address);
    console.log("Balance:", balanceInMatic, "MATIC");
    console.log("Network:", await provider.getNetwork());
}

main();