"""
ANNA Protocol SDK - Python Client
Versão: 1.0.0

SDK oficial para interagir com o ANNA Protocol (Artificial Neural Network for Accountability)
Fornece interface simples para desenvolvedores integrarem seus agentes de IA ao protocolo.

Autor: ANNA Protocol Team
Licença: MIT
"""

import json
import time
import hashlib
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
import requests


# ============================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================

NETWORKS = {
    "polygon-amoy": {
        "rpc": "https://rpc-amoy.polygon.technology/",
        "chain_id": 80002,
        "explorer": "https://www.oklink.com/amoy"
    },
    "polygon-mainnet": {
        "rpc": "https://polygon-rpc.com",
        "chain_id": 137,
        "explorer": "https://polygonscan.com"
    }
}


# ============================================================
# TIPOS E ENUMS
# ============================================================

class VerificationTier(Enum):
    """Níveis de verificação disponíveis"""
    BASIC = "basic"  # Tier 1: Verificação determinística
    STANDARD = "standard"  # Tier 1 + Tier 2: Verificação semântica
    PREMIUM = "premium"  # Tier 1 + 2 + 3: Verificação por especialistas


class AttestationStatus(Enum):
    """Status possíveis de uma attestation"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    CHALLENGED = "challenged"


@dataclass
class ReasoningStep:
    """Estrutura de um passo de raciocínio"""
    step_number: int
    description: str
    rationale: str


@dataclass
class Reasoning:
    """Estrutura completa de raciocínio"""
    input: str
    reasoning_steps: List[ReasoningStep]
    conclusion: str
    confidence: float
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "input": self.input,
            "reasoning_steps": [
                {
                    "step_number": step.step_number,
                    "description": step.description,
                    "rationale": step.rationale
                }
                for step in self.reasoning_steps
            ],
            "conclusion": self.conclusion,
            "confidence": self.confidence
        }


@dataclass
class AttestationResult:
    """Resultado de uma attestation"""
    attestation_id: str
    tx_hash: str
    status: AttestationStatus
    timestamp: int
    explorer_url: str
    
    # Informações de verificação (quando disponível)
    verified: bool = False
    score: Optional[int] = None
    verifier: Optional[str] = None
    verification_time: Optional[int] = None


@dataclass
class Identity:
    """Identidade de um agente"""
    agent_id: int
    did: str
    address: str
    model_type: str
    model_version: str
    specializations: List[str]
    creation_time: int
    token_uri: Optional[str] = None


# ============================================================
# CLIENTE PRINCIPAL
# ============================================================

class ANNAClient:
    """
    Cliente principal do ANNA Protocol SDK
    
    Uso básico:
    ```python
    from anna_sdk import ANNAClient, Reasoning, ReasoningStep
    
    # Inicializar cliente
    client = ANNAClient(
        private_key="0x...",
        network="polygon-amoy"
    )
    
    # Registrar identidade (primeira vez)
    identity = client.register_identity(
        model_type="LLM",
        model_version="gpt-4",
        specializations=["legal", "contracts"]
    )
    
    # Criar reasoning
    reasoning = Reasoning(
        input="Generate NDA contract",
        reasoning_steps=[
            ReasoningStep(1, "Analyzed requirements", "User needs NDA"),
            ReasoningStep(2, "Applied legal framework", "Used standard NDA template")
        ],
        conclusion="Contract generated successfully",
        confidence=0.95
    )
    
    # Submeter attestation
    result = client.submit_attestation(
        content="contract text here...",
        reasoning=reasoning,
        category="legal-contract"
    )
    
    print(f"Attestation ID: {result.attestation_id}")
    print(f"View at: {result.explorer_url}")
    ```
    """
    
    def __init__(
        self,
        private_key: str,
        network: str = "polygon-amoy",
        identity_contract: Optional[str] = None,
        attestation_contract: Optional[str] = None,
        reputation_contract: Optional[str] = None
    ):
        """
        Inicializa o cliente ANNA
        
        Args:
            private_key: Chave privada da wallet do agente (com 0x)
            network: Rede blockchain ("polygon-amoy" ou "polygon-mainnet")
            identity_contract: Endereço do contrato AnnaIdentity (opcional)
            attestation_contract: Endereço do contrato AnnaAttestation (opcional)
            reputation_contract: Endereço do contrato AnnaReputation (opcional)
        """
        # Validar network
        if network not in NETWORKS:
            raise ValueError(f"Network inválida. Use: {list(NETWORKS.keys())}")
        
        # Configurar Web3
        self.network = network
        self.network_config = NETWORKS[network]
        self.w3 = Web3(Web3.HTTPProvider(self.network_config["rpc"]))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Não foi possível conectar ao RPC: {self.network_config['rpc']}")
        
        # Configurar conta
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # Endereços dos contratos
        self.identity_contract = identity_contract
        self.attestation_contract = attestation_contract
        self.reputation_contract = reputation_contract
        
        # Carregar ABIs (simplificado - em produção, carregar de arquivo)
        self._load_abis()
        
        # Inicializar contratos
        if self.identity_contract:
            self.identity = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.identity_contract),
                abi=self.identity_abi
            )
        
        if self.attestation_contract:
            self.attestation = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.attestation_contract),
                abi=self.attestation_abi
            )
        
        if self.reputation_contract:
            self.reputation = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.reputation_contract),
                abi=self.reputation_abi
            )
    
    def _load_abis(self):
        """Carrega ABIs dos contratos (versão simplificada)"""
        # Em produção, carregar de arquivos JSON
        # Por enquanto, definindo ABIs mínimas necessárias
        
        self.identity_abi = [
            {
                "inputs": [
                    {"name": "modelType", "type": "string"},
                    {"name": "modelVersion", "type": "string"},
                    {"name": "specializations", "type": "string[]"}
                ],
                "name": "registerAgent",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentAddress", "type": "address"}],
                "name": "agentIdByAddress",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.attestation_abi = [
            {
                "inputs": [
                    {"name": "contractHash", "type": "bytes32"},
                    {"name": "reasoningHash", "type": "bytes32"},
                    {"name": "modelVersion", "type": "string"},
                    {"name": "category", "type": "string"},
                    {"name": "signature", "type": "bytes"}
                ],
                "name": "submitAttestation",
                "outputs": [{"name": "", "type": "bytes32"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "", "type": "bytes32"}],
                "name": "attestations",
                "outputs": [
                    {"name": "contractHash", "type": "bytes32"},
                    {"name": "reasoningHash", "type": "bytes32"},
                    {"name": "agent", "type": "address"},
                    {"name": "modelVersion", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "status", "type": "uint8"},
                    {"name": "consistencyScore", "type": "uint8"},
                    {"name": "verifier", "type": "address"},
                    {"name": "verificationTime", "type": "uint256"},
                    {"name": "category", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.reputation_abi = [
            {
                "inputs": [{"name": "agentAddress", "type": "address"}],
                "name": "getReputationScore",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def register_identity(
        self,
        model_type: str,
        model_version: str,
        specializations: List[str],
        wait_for_confirmation: bool = True
    ) -> Identity:
        """
        Registra a identidade do agente (apenas primeira vez)
        
        Args:
            model_type: Tipo do modelo (ex: "LLM", "Vision", "Multimodal")
            model_version: Versão do modelo (ex: "gpt-4-turbo")
            specializations: Lista de especializações (ex: ["legal", "contracts"])
            wait_for_confirmation: Aguardar confirmação on-chain
        
        Returns:
            Identity: Objeto com informações da identidade criada
        
        Raises:
            ValueError: Se já tiver identidade registrada
            Exception: Se houver erro na transação
        """
        if not self.identity_contract:
            raise ValueError("Endereço do contrato Identity não configurado")
        
        # Verificar se já tem identidade
        agent_id = self.identity.functions.agentIdByAddress(self.address).call()
        if agent_id != 0:
            raise ValueError(f"Agente já registrado com ID: {agent_id}")
        
        # Preparar transação
        tx = self.identity.functions.registerAgent(
            model_type,
            model_version,
            specializations
        ).build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Assinar e enviar
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        if wait_for_confirmation:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt['status'] != 1:
                raise Exception("Transação falhou")
            
            # Buscar agent_id criado
            agent_id = self.identity.functions.agentIdByAddress(self.address).call()
        
        # Construir DID
        did = f"did:anna:{self.address.lower()}"
        
        return Identity(
            agent_id=agent_id if wait_for_confirmation else 0,
            did=did,
            address=self.address,
            model_type=model_type,
            model_version=model_version,
            specializations=specializations,
            creation_time=int(time.time())
        )
    
    def submit_attestation(
        self,
        content: str,
        reasoning: Reasoning,
        category: str,
        tier: str = "basic",
        wait_for_confirmation: bool = True
    ) -> AttestationResult:
        """
        Submete uma attestation ao protocolo
        
        Args:
            content: Conteúdo a ser atestado (contrato, decisão, etc)
            reasoning: Objeto Reasoning com o raciocínio estruturado
            category: Categoria da attestation (ex: "legal-contract", "financial-decision")
            tier: Nível de verificação ("basic", "standard", "premium")
            wait_for_confirmation: Aguardar confirmação on-chain
        
        Returns:
            AttestationResult: Resultado da submissão
        
        Raises:
            ValueError: Se parâmetros inválidos
            Exception: Se houver erro na transação
        """
        if not self.attestation_contract:
            raise ValueError("Endereço do contrato Attestation não configurado")
        
        # Validar reasoning
        if not 0 <= reasoning.confidence <= 1:
            raise ValueError("Confidence deve estar entre 0 e 1")
        
        if len(reasoning.reasoning_steps) == 0:
            raise ValueError("Reasoning deve ter pelo menos 1 step")
        
        # Calcular hashes
        content_hash = Web3.keccak(text=content)
        reasoning_dict = reasoning.to_dict()
        reasoning_json = json.dumps(reasoning_dict, sort_keys=True)
        reasoning_hash = Web3.keccak(text=reasoning_json)
        
        # Obter model version
        agent_id = self.identity.functions.agentIdByAddress(self.address).call()
        if agent_id == 0:
            raise ValueError("Agente não registrado. Execute register_identity() primeiro.")
        
        model_version = "v1.0"  # Em produção, buscar do contrato Identity
        
        # Preparar dados para assinatura EIP-712
        domain_data = {
            "name": "ANNA Protocol",
            "version": "1",
            "chainId": self.network_config["chain_id"],
            "verifyingContract": self.attestation_contract
        }
        
        message_types = {
            "Attestation": [
                {"name": "contractHash", "type": "bytes32"},
                {"name": "reasoningHash", "type": "bytes32"},
                {"name": "agent", "type": "address"},
                {"name": "modelVersion", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "category", "type": "string"}
            ]
        }
        
        timestamp = int(time.time())
        
        message_data = {
            "contractHash": content_hash,
            "reasoningHash": reasoning_hash,
            "agent": self.address,
            "modelVersion": model_version,
            "timestamp": timestamp,
            "category": category
        }
        
        # Assinar com EIP-712
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                **message_types
            },
            "primaryType": "Attestation",
            "domain": domain_data,
            "message": message_data
        }
        
        encoded_data = encode_typed_data(full_message=typed_data)
        signature = self.account.sign_message(encoded_data).signature
        
        # Preparar transação
        tx = self.attestation.functions.submitAttestation(
            content_hash,
            reasoning_hash,
            model_version,
            category,
            signature
        ).build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Assinar e enviar
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        # Calcular attestation_id (mesmo cálculo do contrato)
        attestation_id = Web3.keccak(
            Web3.solidity_keccak(['bytes32', 'bytes32', 'address', 'uint256'],
                                [content_hash, reasoning_hash, self.address, timestamp])
        ).hex()
        
        if wait_for_confirmation:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt['status'] != 1:
                raise Exception("Transação falhou")
        
        # Construir URL do explorer
        explorer_url = f"{self.network_config['explorer']}/tx/{tx_hash_hex}"
        
        return AttestationResult(
            attestation_id=attestation_id,
            tx_hash=tx_hash_hex,
            status=AttestationStatus.PENDING,
            timestamp=timestamp,
            explorer_url=explorer_url
        )
    
    def get_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """
        Busca informações de uma attestation
        
        Args:
            attestation_id: ID da attestation (bytes32 hex)
        
        Returns:
            Dict com dados da attestation
        """
        if not self.attestation_contract:
            raise ValueError("Endereço do contrato Attestation não configurado")
        
        attestation_data = self.attestation.functions.attestations(attestation_id).call()
        
        return {
            "contract_hash": attestation_data[0].hex(),
            "reasoning_hash": attestation_data[1].hex(),
            "agent": attestation_data[2],
            "model_version": attestation_data[3],
            "timestamp": attestation_data[4],
            "status": AttestationStatus(attestation_data[5]),
            "consistency_score": attestation_data[6],
            "verifier": attestation_data[7],
            "verification_time": attestation_data[8],
            "category": attestation_data[9]
        }
    
    def wait_for_verification(
        self,
        attestation_id: str,
        timeout: int = 60,
        poll_interval: int = 5
    ) -> AttestationResult:
        """
        Aguarda a verificação de uma attestation
        
        Args:
            attestation_id: ID da attestation
            timeout: Tempo máximo de espera em segundos
            poll_interval: Intervalo entre checks em segundos
        
        Returns:
            AttestationResult com resultado da verificação
        
        Raises:
            TimeoutError: Se exceder o timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            attestation = self.get_attestation(attestation_id)
            
            if attestation["status"] != AttestationStatus.PENDING:
                return AttestationResult(
                    attestation_id=attestation_id,
                    tx_hash="",  # Não temos o tx_hash da verificação aqui
                    status=attestation["status"],
                    timestamp=attestation["timestamp"],
                    explorer_url=f"{self.network_config['explorer']}/address/{self.attestation_contract}",
                    verified=attestation["status"] == AttestationStatus.VERIFIED,
                    score=attestation["consistency_score"],
                    verifier=attestation["verifier"],
                    verification_time=attestation["verification_time"]
                )
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Verificação não concluída em {timeout}s")
    
    def get_reputation(self, agent_address: Optional[str] = None) -> int:
        """
        Busca o score de reputação de um agente
        
        Args:
            agent_address: Endereço do agente (se None, usa o próprio)
        
        Returns:
            Score de reputação (0-1000)
        """
        if not self.reputation_contract:
            raise ValueError("Endereço do contrato Reputation não configurado")
        
        address = agent_address or self.address
        score = self.reputation.functions.getReputationScore(address).call()
        return score
    
    def get_balance(self) -> float:
        """
        Retorna o saldo de MATIC da wallet
        
        Returns:
            Saldo em MATIC
        """
        balance_wei = self.w3.eth.get_balance(self.address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_identity(self, address: Optional[str] = None) -> Optional[Dict]:
        """
        Busca informações de identidade de um agente
        
        Args:
            address: Endereço do agente (se None, usa o próprio)
        
        Returns:
            Dict com dados da identidade ou None se não registrado
        """
        if not self.identity_contract:
            raise ValueError("Endereço do contrato Identity não configurado")
        
        addr = address or self.address
        agent_id = self.identity.functions.agentIdByAddress(addr).call()
        
        if agent_id == 0:
            return None
        
        # Em produção, buscar mais dados do contrato
        return {
            "agent_id": agent_id,
            "did": f"did:anna:{addr.lower()}",
            "address": addr
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_reasoning(
    input_text: str,
    steps: List[Tuple[str, str]],
    conclusion: str,
    confidence: float
) -> Reasoning:
    """
    Helper para criar objeto Reasoning facilmente
    
    Args:
        input_text: Texto de entrada
        steps: Lista de tuplas (description, rationale)
        conclusion: Conclusão final
        confidence: Nível de confiança (0-1)
    
    Returns:
        Reasoning object
    
    Example:
        >>> reasoning = create_reasoning(
        ...     "Generate NDA",
        ...     [
        ...         ("Analyzed requirements", "User needs NDA"),
        ...         ("Applied legal framework", "Used standard template")
        ...     ],
        ...     "Contract generated",
        ...     0.95
        ... )
    """
    reasoning_steps = [
        ReasoningStep(i + 1, desc, rat)
        for i, (desc, rat) in enumerate(steps)
    ]
    
    return Reasoning(
        input=input_text,
        reasoning_steps=reasoning_steps,
        conclusion=conclusion,
        confidence=confidence
    )


def calculate_content_hash(content: str) -> str:
    """
    Calcula hash Keccak256 de um conteúdo
    
    Args:
        content: Conteúdo a ser hasheado
    
    Returns:
        Hash em formato hexadecimal
    """
    return Web3.keccak(text=content).hex()


# ============================================================
# EXCEÇÕES CUSTOMIZADAS
# ============================================================

class ANNAError(Exception):
    """Erro base do SDK"""
    pass


class IdentityNotFoundError(ANNAError):
    """Agente não tem identidade registrada"""
    pass


class AttestationNotFoundError(ANNAError):
    """Attestation não encontrada"""
    pass


class VerificationTimeoutError(ANNAError):
    """Timeout aguardando verificação"""
    pass


# ============================================================
# VERSÃO DO SDK
# ============================================================

__version__ = "1.0.0"
__author__ = "ANNA Protocol Team"
__license__ = "MIT"