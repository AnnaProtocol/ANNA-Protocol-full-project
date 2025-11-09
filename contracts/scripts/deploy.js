const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying ANNA Protocol contracts...\n");

  // Deploy AnnaIdentity
  console.log("1️⃣ Deploying AnnaIdentity...");
  const AnnaIdentity = await hre.ethers.getContractFactory("AnnaIdentity");
  const identity = await AnnaIdentity.deploy();
  await identity.waitForDeployment();
  const identityAddress = await identity.getAddress();
  console.log("✅ AnnaIdentity deployed to:", identityAddress);

  // Deploy AnnaAttestation
  console.log("\n2️⃣ Deploying AnnaAttestation...");
  const AnnaAttestation = await hre.ethers.getContractFactory("AnnaAttestation");
  const attestation = await AnnaAttestation.deploy(identityAddress);
  await attestation.waitForDeployment();
  const attestationAddress = await attestation.getAddress();
  console.log("✅ AnnaAttestation deployed to:", attestationAddress);

  // Deploy AnnaReputation
  console.log("\n3️⃣ Deploying AnnaReputation...");
  const AnnaReputation = await hre.ethers.getContractFactory("AnnaReputation");
  const reputation = await AnnaReputation.deploy(attestationAddress);
  await reputation.waitForDeployment();
  const reputationAddress = await reputation.getAddress();
  console.log("✅ AnnaReputation deployed to:", reputationAddress);

  console.log("\n📝 Deployment Summary:");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("AnnaIdentity:    ", identityAddress);
  console.log("AnnaAttestation: ", attestationAddress);
  console.log("AnnaReputation:  ", reputationAddress);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

  // Save addresses
  const fs = require('fs');
  const addresses = {
    identity: identityAddress,
    attestation: attestationAddress,
    reputation: reputationAddress,
    network: hre.network.name,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync(
    'deployed-addresses.json',
    JSON.stringify(addresses, null, 2)
  );
  console.log("💾 Addresses saved to deployed-addresses.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });