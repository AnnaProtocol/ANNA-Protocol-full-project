const hre = require("hardhat");

async function main() {
  console.log("🔐 Autorizando verificador...\n");

  // Endereços
  const ATTESTATION_CONTRACT = "0xEd98b7Ed960924cEf4d5dfF174252CE88DeCb4e8";
  const VERIFIER_ADDRESS = "0x25e6CA2E68726D818f43a67C93b9627b285C1892";

  // Conectar ao contrato
  const attestation = await hre.ethers.getContractAt("AnnaAttestation", ATTESTATION_CONTRACT);

  console.log("📝 Contrato AnnaAttestation:", ATTESTATION_CONTRACT);
  console.log("👤 Verificador:", VERIFIER_ADDRESS);
  console.log();

  // Verificar se já está autorizado
  const isAuthorizedBefore = await attestation.authorizedVerifiers(VERIFIER_ADDRESS);
  console.log("Status atual:", isAuthorizedBefore ? "✅ JÁ AUTORIZADO" : "⏳ NÃO AUTORIZADO");

  if (isAuthorizedBefore) {
    console.log("\n✨ Verificador já está autorizado! Nada a fazer.");
    return;
  }

  // Autorizar verificador
  console.log("\n⏳ Autorizando verificador...");
  const tx = await attestation.addVerifier(VERIFIER_ADDRESS);
  console.log("📤 TX enviada:", tx.hash);
  
  console.log("⏳ Aguardando confirmação...");
  await tx.wait();
  
  // Verificar novamente
  const isAuthorizedAfter = await attestation.authorizedVerifiers(VERIFIER_ADDRESS);
  
  if (isAuthorizedAfter) {
    console.log("\n✅ SUCESSO! Verificador autorizado!");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log("🎉 O verificador agora pode submeter verificações!");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
  } else {
    console.log("\n❌ Erro: Verificador não foi autorizado!");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });