// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AnnaIdentity
 * @dev Soulbound NFT para identidade de agentes de IA
 * Não transferível após mint - identidade permanente
 */
contract AnnaIdentity is ERC721, Ownable {
    
    struct AgentMetadata {
        string did;              // Decentralized Identifier
        string modelType;        // Ex: "LLM", "Computer Vision"
        string modelVersion;     // Ex: "gpt-4-turbo-2024"
        address operator;        // Endereço da entidade operadora
        string[] specializations; // Áreas de atuação
        uint256 registrationDate;
        bool isActive;           // Permite desativar sem queimar NFT
    }
    
    uint256 private _tokenIdCounter;
    mapping(uint256 => AgentMetadata) public agentMetadata;
    mapping(address => uint256) public agentIdByAddress;
    
    event AgentRegistered(
        uint256 indexed tokenId,
        address indexed agentAddress,
        string did
    );
    
    event AgentDeactivated(uint256 indexed tokenId);
    event AgentReactivated(uint256 indexed tokenId);
    
    constructor() ERC721("ANNA Agent Identity", "ANNA-ID") Ownable(msg.sender) {}
    
    /**
     * @dev Registra novo agente de IA
     */
    function registerAgent(
        address agentAddress,
        string memory did,
        string memory modelType,
        string memory modelVersion,
        string[] memory specializations
    ) external returns (uint256) {
        require(agentIdByAddress[agentAddress] == 0, "Agent already registered");
        
        uint256 tokenId = ++_tokenIdCounter;
        _safeMint(agentAddress, tokenId);
        
        agentMetadata[tokenId] = AgentMetadata({
            did: did,
            modelType: modelType,
            modelVersion: modelVersion,
            operator: msg.sender,
            specializations: specializations,
            registrationDate: block.timestamp,
            isActive: true
        });
        
        agentIdByAddress[agentAddress] = tokenId;
        
        emit AgentRegistered(tokenId, agentAddress, did);
        return tokenId;
    }
    
    /**
     * @dev Desativa agente
     */
    function deactivateAgent(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender || owner() == msg.sender, "Not authorized");
        agentMetadata[tokenId].isActive = false;
        emit AgentDeactivated(tokenId);
    }
    
    /**
     * @dev Reativa agente
     */
    function reactivateAgent(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender || owner() == msg.sender, "Not authorized");
        agentMetadata[tokenId].isActive = true;
        emit AgentReactivated(tokenId);
    }
    
    /**
     * @dev Override para tornar NFT não transferível (Soulbound)
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal virtual override returns (address) {
        address from = _ownerOf(tokenId);
        if (from != address(0) && to != address(0)) {
            revert("Soulbound: Transfer not allowed");
        }
        return super._update(to, tokenId, auth);
    }
    
    /**
     * @dev Retorna metadados completos de um agente
     */
    function getAgentMetadata(uint256 tokenId) 
        external 
        view 
        returns (AgentMetadata memory) 
    {
        require(_ownerOf(tokenId) != address(0), "Agent does not exist");
        return agentMetadata[tokenId];
    }
    
    /**
     * @dev Total de agentes registrados
     */
    function totalAgents() external view returns (uint256) {
        return _tokenIdCounter;
    }
}