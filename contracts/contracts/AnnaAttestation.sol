// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AnnaIdentity.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title AnnaAttestation
 * @dev Registro de decisões e raciocínios de agentes de IA
 */
contract AnnaAttestation {
    using ECDSA for bytes32;
    
    enum Status { Pending, Verified, Rejected, Challenged }
    
    struct Attestation {
        bytes32 contentHash;
        bytes32 reasoningHash;
        address agent;
        string modelVersion;
        uint256 timestamp;
        Status status;
        uint8 consistencyScore;
        address verifier;
        uint256 verificationTime;
        string category;
    }
    
    AnnaIdentity public identityContract;
    
    mapping(bytes32 => Attestation) public attestations;
    mapping(address => uint256) public attestationCount;
    mapping(address => bool) public authorizedVerifiers;
    
    event AttestationSubmitted(
        bytes32 indexed attestationId,
        address indexed agent,
        string category,
        uint256 timestamp
    );
    
    event AttestationVerified(
        bytes32 indexed attestationId,
        address indexed verifier,
        Status status,
        uint8 consistencyScore
    );
    
    event AttestationChallenged(
        bytes32 indexed attestationId,
        address indexed challenger,
        string reason
    );
    
    constructor(address _identityContract) {
        identityContract = AnnaIdentity(_identityContract);
    }
    
    /**
     * @dev Submete nova attestation
     */
    function submitAttestation(
        bytes32 contentHash,
        bytes32 reasoningHash,
        string calldata modelVersion,
        string calldata category
    ) external returns (bytes32) {
        require(
            identityContract.agentIdByAddress(msg.sender) != 0,
            "Agent not registered"
        );
        
        bytes32 attestationId = keccak256(
            abi.encodePacked(
                contentHash,
                reasoningHash,
                msg.sender,
                block.timestamp
            )
        );
        
        require(
            attestations[attestationId].timestamp == 0,
            "Attestation already exists"
        );
        
        attestations[attestationId] = Attestation({
            contentHash: contentHash,
            reasoningHash: reasoningHash,
            agent: msg.sender,
            modelVersion: modelVersion,
            timestamp: block.timestamp,
            status: Status.Pending,
            consistencyScore: 0,
            verifier: address(0),
            verificationTime: 0,
            category: category
        });
        
        attestationCount[msg.sender]++;
        
        emit AttestationSubmitted(attestationId, msg.sender, category, block.timestamp);
        return attestationId;
    }
    
    /**
     * @dev Verifica attestation (apenas verificadores autorizados)
     */
    function verifyAttestation(
        bytes32 attestationId,
        bool passed,
        uint8 consistencyScore
    ) external {
        require(authorizedVerifiers[msg.sender], "Not authorized verifier");
        require(consistencyScore <= 100, "Invalid score");
        
        Attestation storage att = attestations[attestationId];
        require(att.timestamp != 0, "Attestation does not exist");
        require(att.status == Status.Pending, "Already verified");
        
        att.status = passed ? Status.Verified : Status.Rejected;
        att.consistencyScore = consistencyScore;
        att.verifier = msg.sender;
        att.verificationTime = block.timestamp;
        
        emit AttestationVerified(attestationId, msg.sender, att.status, consistencyScore);
    }
    
    /**
     * @dev Permite contestar uma verificação
     */
    function challengeAttestation(
        bytes32 attestationId,
        string calldata reason
    ) external {
        Attestation storage att = attestations[attestationId];
        require(
            att.status == Status.Verified || att.status == Status.Rejected,
            "Not verified yet"
        );
        require(
            block.timestamp <= att.verificationTime + 7 days,
            "Challenge period expired"
        );
        
        att.status = Status.Challenged;
        emit AttestationChallenged(attestationId, msg.sender, reason);
    }
    
    /**
     * @dev Adiciona verificador autorizado
     */
    function addVerifier(address verifier) external {
        authorizedVerifiers[verifier] = true;
    }
    
    /**
     * @dev Remove verificador
     */
    function removeVerifier(address verifier) external {
        authorizedVerifiers[verifier] = false;
    }
    
    /**
     * @dev Retorna attestation completa
     */
    function getAttestation(bytes32 attestationId) 
        external 
        view 
        returns (Attestation memory) 
    {
        require(attestations[attestationId].timestamp != 0, "Attestation does not exist");
        return attestations[attestationId];
    }
}