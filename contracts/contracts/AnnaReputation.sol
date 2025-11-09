// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AnnaAttestation.sol";

/**
 * @title AnnaReputation
 * @dev Cálculo e gestão de reputação de agentes
 */
contract AnnaReputation {
    
    AnnaAttestation public attestationContract;
    
    struct ReputationData {
        uint256 totalAttestations;
        uint256 verifiedAttestations;
        uint256 rejectedAttestations;
        uint256 averageConsistencyScore;
        uint256 registrationTime;
        uint256 lastUpdateTime;
    }
    
    mapping(address => ReputationData) public reputationData;
    mapping(address => uint256) public reputationScore;
    
    // Pesos para cálculo (em pontos base, 1000 = 100%)
    uint256 public constant VOLUME_WEIGHT = 300;
    uint256 public constant CONSISTENCY_WEIGHT = 400;
    uint256 public constant AGE_WEIGHT = 150;
    uint256 public constant PENALTY_WEIGHT = 500;
    
    event ReputationUpdated(
        address indexed agent,
        uint256 newScore,
        uint256 timestamp
    );
    
    constructor(address _attestationContract) {
        attestationContract = AnnaAttestation(_attestationContract);
    }
    
    /**
     * @dev Atualiza dados de reputação após verificação
     */
    function updateReputation(address agent, bytes32 attestationId) external {
        AnnaAttestation.Attestation memory att = attestationContract.getAttestation(attestationId);
        
        ReputationData storage data = reputationData[agent];
        
        if (data.registrationTime == 0) {
            data.registrationTime = block.timestamp;
        }
        
        data.totalAttestations++;
        
        if (att.status == AnnaAttestation.Status.Verified) {
            data.verifiedAttestations++;
            
            uint256 totalScore = data.averageConsistencyScore * (data.verifiedAttestations - 1);
            data.averageConsistencyScore = (totalScore + att.consistencyScore) / data.verifiedAttestations;
            
        } else if (att.status == AnnaAttestation.Status.Rejected) {
            data.rejectedAttestations++;
        }
        
        data.lastUpdateTime = block.timestamp;
        
        uint256 newScore = _calculateScore(agent);
        reputationScore[agent] = newScore;
        
        emit ReputationUpdated(agent, newScore, block.timestamp);
    }
    
    /**
     * @dev Calcula score de reputação
     */
    function _calculateScore(address agent) internal view returns (uint256) {
        ReputationData memory data = reputationData[agent];
        
        if (data.totalAttestations == 0) return 0;
        
        // Volume Score (logarítmico)
        uint256 volumeScore = _log2(data.verifiedAttestations + 1) * 10;
        if (volumeScore > 100) volumeScore = 100;
        
        // Consistency Score
        uint256 consistencyScore = data.averageConsistencyScore;
        
        // Age Score (cap em 1 ano)
        uint256 ageInDays = (block.timestamp - data.registrationTime) / 1 days;
        uint256 ageScore = ageInDays > 365 ? 100 : (ageInDays * 100) / 365;
        
        // Penalty Score
        uint256 penaltyScore = data.rejectedAttestations * 10;
        
        uint256 weightedScore = (
            volumeScore * VOLUME_WEIGHT +
            consistencyScore * CONSISTENCY_WEIGHT +
            ageScore * AGE_WEIGHT
        ) / 1000;
        
        uint256 penaltyImpact = (penaltyScore * PENALTY_WEIGHT) / 1000;
        
        if (weightedScore > penaltyImpact) {
            return (weightedScore - penaltyImpact) * 10;
        } else {
            return 0;
        }
    }
    
    /**
     * @dev Aproximação de log2 para inteiros
     */
    function _log2(uint256 x) internal pure returns (uint256) {
        uint256 result = 0;
        while (x > 1) {
            x >>= 1;
            result++;
        }
        return result;
    }
    
    /**
     * @dev Retorna dados completos de reputação
     */
    function getFullReputation(address agent) 
        external 
        view 
        returns (
            uint256 score,
            uint256 totalAttestations,
            uint256 verifiedAttestations,
            uint256 averageConsistency
        ) 
    {
        ReputationData memory data = reputationData[agent];
        return (
            reputationScore[agent],
            data.totalAttestations,
            data.verifiedAttestations,
            data.averageConsistencyScore
        );
    }
}