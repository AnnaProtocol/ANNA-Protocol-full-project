const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ANNA Protocol", function () {
  let identity, attestation, reputation;
  let owner, agent1, agent2, verifier;

  beforeEach(async function () {
    [owner, agent1, agent2, verifier] = await ethers.getSigners();

    // Deploy Identity
    const AnnaIdentity = await ethers.getContractFactory("AnnaIdentity");
    identity = await AnnaIdentity.deploy();
    await identity.waitForDeployment();

    // Deploy Attestation
    const AnnaAttestation = await ethers.getContractFactory("AnnaAttestation");
    attestation = await AnnaAttestation.deploy(await identity.getAddress());
    await attestation.waitForDeployment();

    // Deploy Reputation
    const AnnaReputation = await ethers.getContractFactory("AnnaReputation");
    reputation = await AnnaReputation.deploy(await attestation.getAddress());
    await reputation.waitForDeployment();
  });

  describe("AnnaIdentity", function () {
    it("Should register a new agent", async function () {
      const did = "did:anna:0x123";
      const modelType = "LLM";
      const modelVersion = "gpt-4";
      const specializations = ["legal", "medical"];

      await identity.connect(agent1).registerAgent(
        agent1.address,
        did,
        modelType,
        modelVersion,
        specializations
      );

      const agentId = await identity.agentIdByAddress(agent1.address);
      expect(agentId).to.equal(1);

      const metadata = await identity.getAgentMetadata(agentId);
      expect(metadata.did).to.equal(did);
      expect(metadata.modelType).to.equal(modelType);
      expect(metadata.isActive).to.equal(true);
    });

    it("Should prevent duplicate registration", async function () {
      const did = "did:anna:0x123";
      await identity.connect(agent1).registerAgent(
        agent1.address,
        did,
        "LLM",
        "v1",
        []
      );

      await expect(
        identity.connect(agent1).registerAgent(
          agent1.address,
          did,
          "LLM",
          "v1",
          []
        )
      ).to.be.revertedWith("Agent already registered");
    });

    it("Should deactivate and reactivate agent", async function () {
      await identity.connect(agent1).registerAgent(
        agent1.address,
        "did:anna:0x123",
        "LLM",
        "v1",
        []
      );

      const agentId = await identity.agentIdByAddress(agent1.address);
      
      await identity.connect(agent1).deactivateAgent(agentId);
      let metadata = await identity.getAgentMetadata(agentId);
      expect(metadata.isActive).to.equal(false);

      await identity.connect(agent1).reactivateAgent(agentId);
      metadata = await identity.getAgentMetadata(agentId);
      expect(metadata.isActive).to.equal(true);
    });

    it("Should prevent NFT transfer (Soulbound)", async function () {
      await identity.connect(agent1).registerAgent(
        agent1.address,
        "did:anna:0x123",
        "LLM",
        "v1",
        []
      );

      const agentId = await identity.agentIdByAddress(agent1.address);

      await expect(
        identity.connect(agent1).transferFrom(agent1.address, agent2.address, agentId)
      ).to.be.revertedWith("Soulbound: Transfer not allowed");
    });
  });

  describe("AnnaAttestation", function () {
    beforeEach(async function () {
      // Registrar agente primeiro
      await identity.connect(agent1).registerAgent(
        agent1.address,
        "did:anna:0x123",
        "LLM",
        "v1",
        []
      );

      // Autorizar verificador
      await attestation.connect(owner).addVerifier(verifier.address);
    });

    it("Should submit attestation", async function () {
      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("contract content"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await attestation.connect(agent1).submitAttestation(
        contentHash,
        reasoningHash,
        "v1.0",
        "legal-contract"
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          return attestation.interface.parseLog(log).name === "AttestationSubmitted";
        } catch {
          return false;
        }
      });

      expect(event).to.not.be.undefined;
    });

    it("Should reject attestation from unregistered agent", async function () {
      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("content"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      await expect(
        attestation.connect(agent2).submitAttestation(
          contentHash,
          reasoningHash,
          "v1.0",
          "category"
        )
      ).to.be.revertedWith("Agent not registered");
    });

    it("Should verify attestation", async function () {
      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("content"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await attestation.connect(agent1).submitAttestation(
        contentHash,
        reasoningHash,
        "v1.0",
        "legal-contract"
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          const parsed = attestation.interface.parseLog(log);
          return parsed.name === "AttestationSubmitted";
        } catch {
          return false;
        }
      });

      const attestationId = event.args[0];

      await attestation.connect(verifier).verifyAttestation(
        attestationId,
        true,
        95
      );

      const att = await attestation.getAttestation(attestationId);
      expect(att.status).to.equal(1); // Status.Verified
      expect(att.consistencyScore).to.equal(95);
    });

    it("Should only allow authorized verifiers", async function () {
      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("content"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await attestation.connect(agent1).submitAttestation(
        contentHash,
        reasoningHash,
        "v1.0",
        "category"
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          const parsed = attestation.interface.parseLog(log);
          return parsed.name === "AttestationSubmitted";
        } catch {
          return false;
        }
      });

      const attestationId = event.args[0];

      await expect(
        attestation.connect(agent2).verifyAttestation(attestationId, true, 90)
      ).to.be.revertedWith("Not authorized verifier");
    });
  });

  describe("AnnaReputation", function () {
    let attestationId;

    beforeEach(async function () {
      // Setup completo
      await identity.connect(agent1).registerAgent(
        agent1.address,
        "did:anna:0x123",
        "LLM",
        "v1",
        []
      );

      await attestation.connect(owner).addVerifier(verifier.address);

      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("content"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await attestation.connect(agent1).submitAttestation(
        contentHash,
        reasoningHash,
        "v1.0",
        "legal"
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          const parsed = attestation.interface.parseLog(log);
          return parsed.name === "AttestationSubmitted";
        } catch {
          return false;
        }
      });

      attestationId = event.args[0];

      await attestation.connect(verifier).verifyAttestation(
        attestationId,
        true,
        90
      );
    });

    it("Should update reputation after verification", async function () {
      await reputation.updateReputation(agent1.address, attestationId);

      const score = await reputation.reputationScore(agent1.address);
      expect(score).to.be.greaterThan(0);

      const data = await reputation.reputationData(agent1.address);
      expect(data.totalAttestations).to.equal(1);
      expect(data.verifiedAttestations).to.equal(1);
      expect(data.averageConsistencyScore).to.equal(90);
    });

    it("Should calculate reputation correctly", async function () {
      await reputation.updateReputation(agent1.address, attestationId);

      const fullRep = await reputation.getFullReputation(agent1.address);
      
      expect(fullRep.score).to.be.greaterThan(0);
      expect(fullRep.totalAttestations).to.equal(1);
      expect(fullRep.verifiedAttestations).to.equal(1);
      expect(fullRep.averageConsistency).to.equal(90);
    });
  });

  describe("Integration Test", function () {
    it("Should complete full workflow", async function () {
      // 1. Registrar agente
      await identity.connect(agent1).registerAgent(
        agent1.address,
        "did:anna:0x123",
        "LLM",
        "gpt-4",
        ["legal", "medical"]
      );

      // 2. Autorizar verificador
      await attestation.connect(owner).addVerifier(verifier.address);

      // 3. Submeter attestation
      const contentHash = ethers.keccak256(ethers.toUtf8Bytes("Legal Contract NDA"));
      const reasoningHash = ethers.keccak256(
        ethers.toUtf8Bytes(JSON.stringify({
          input: "Generate NDA",
          steps: ["Identify parties", "Add clauses"],
          conclusion: "NDA generated",
          confidence: 0.95
        }))
      );

      const tx = await attestation.connect(agent1).submitAttestation(
        contentHash,
        reasoningHash,
        "v1.0",
        "legal-contract"
      );

      // 4. Verificar
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          const parsed = attestation.interface.parseLog(log);
          return parsed.name === "AttestationSubmitted";
        } catch {
          return false;
        }
      });

      const attestationId = event.args[0];

      await attestation.connect(verifier).verifyAttestation(
        attestationId,
        true,
        95
      );

      // 5. Atualizar reputação
      await reputation.updateReputation(agent1.address, attestationId);

      // 6. Verificar resultado final
      const score = await reputation.reputationScore(agent1.address);
      const att = await attestation.getAttestation(attestationId);
      const agentId = await identity.agentIdByAddress(agent1.address);

      expect(agentId).to.equal(1);
      expect(att.status).to.equal(1); // Verified
      expect(score).to.be.greaterThan(0);

      console.log("\n✅ WORKFLOW COMPLETO:");
      console.log("   Agent ID:", agentId.toString());
      console.log("   Attestation Status: Verified");
      console.log("   Reputation Score:", score.toString());
    });
  });
});