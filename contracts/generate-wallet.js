const { ethers } = require("ethers");

const wallet = ethers.Wallet.createRandom();

console.log("\n🔑 Nova Wallet Criada!\n");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("Address:0x25e6CA2E68726D818f43a67C93b9627b285C1892", wallet.address);
console.log("Private Key:0x455811470afedd3b73bfee7f1b7f7727b3c644ec4f24df5a0be5d2a3907120c8", wallet.privateKey);
console.log("Mnemonic:display ribbon select arena frame tuna boss violin quality rice coyote like", wallet.mnemonic.phrase);
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
console.log("⚠️  NUNCA compartilhe sua private key!");
console.log("💾 Salve em local seguro!\n");