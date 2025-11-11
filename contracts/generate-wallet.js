require("dotenv").config();

const { ethers } = require("ethers");

const wallet = ethers.Wallet.createRandom();
const privateKey = process.env.PRIVATE_KEY;
const mnemonic = process.env.MNEMONIC;

console.log("\n🔑 Nova Wallet Criada!\n");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("Address:0x25e6CA2E68726D818f43a67C93b9627b285C1892", wallet.address);
console.log("🔑 Private Key:", privateKey);
console.log("🧠 Mnemonic:", mnemonic);
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
console.log("⚠️  NUNCA compartilhe sua private key!");
console.log("💾 Salve em local seguro!\n");