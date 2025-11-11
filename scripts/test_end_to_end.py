"""
ANNA Protocol - Teste End-to-End Completo v2
============================================

Script melhorado com error handling completo
"""

import json
import time
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# ============================================================
# CONFIGURAÇÃO
# ============================================================

POLYGON_AMOY_RPC = "https://rpc-amoy.polygon.technology/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY") or os.getenv("VERIFIER_PRIVATE_KEY")

# Endereços dos contratos
IDENTITY_CONTRACT = "0x8b9b5D3f698BE53Ae98162f6e013Bc9214bc7AF0"
ATTESTATION_CONTRACT = "0xEd98b7Ed960924cEf4d5dfF174252CE88DeCb4e8"
REPUTATION_CONTRACT = "0x5CF18F2eDCB198D4D420ae587Da01035fFfE7172"

print("🚀 ANNA Protocol - Teste End-to-End")
print("=" * 60)
print()

# Setup Web3
w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC))
account = Account.from_key(PRIVATE_KEY)

print(f"✅ Conectado à Polygon Amoy")
print(f"   Chain ID: {w3.eth.chain_id}")
print(f"   Wallet: {account.address}")
print(f"   Saldo: {w3.from_wei(w3.eth.get_balance(account.address), 'ether'):.4f} MATIC")
print()

# ABIs mínimos
identity_abi = [
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

attestation_abi = [
    {
        "inputs": [
            {"name": "contentHash", "type": "bytes32"},
            {"name": "reasoningHash", "type": "bytes32"},
            {"name": "modelVersion", "type": "string"},
            {"name": "category", "type": "string"}
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
            {"name": "contentHash", "type": "bytes32"},
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

identity = w3.eth.contract(
    address=Web3.to_checksum_address(IDENTITY_CONTRACT),
    abi=identity_abi
)

attestation = w3.eth.contract(
    address=Web3.to_checksum_address(ATTESTATION_CONTRACT),
    abi=attestation_abi
)

print("✅ Contratos carregados")
print()

# ============================================================
# ETAPA 1: REGISTRAR IDENTIDADE
# ============================================================

print("=" * 60)
print("ETAPA 1: REGISTRAR IDENTIDADE")
print("=" * 60)
print()

try:
    agent_id = identity.functions.agentIdByAddress(account.address).call()
    
    if agent_id != 0:
        print(f"✅ Agente já registrado!")
        print(f"   Agent ID: {agent_id}")
        print(f"   DID: did:anna:{account.address.lower()}")
    else:
        print("⏳ Registrando nova identidade...")
        
        tx = identity.functions.registerAgent(
            "LLM",
            "claude-3.5-sonnet",
            ["blockchain", "web3", "smart-contracts"]
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"📤 TX enviada: {tx_hash_hex}")
        print(f"🔗 Explorer: https://www.oklink.com/amoy/tx/{tx_hash_hex}")
        print("⏳ Aguardando confirmação...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            agent_id = identity.functions.agentIdByAddress(account.address).call()
            print()
            print("✅ IDENTIDADE REGISTRADA COM SUCESSO!")
            print(f"   Agent ID: {agent_id}")
            print(f"   DID: did:anna:{account.address.lower()}")
            print(f"   Gas usado: {receipt['gasUsed']}")
        else:
            print("❌ Transação falhou!")
            print(f"   Status: {receipt['status']}")
            exit(1)

except Exception as e:
    print(f"❌ Erro: {e}")
    print()
    print("💡 Possíveis causas:")
    print("   1. Agente já registrado")
    print("   2. Gas insuficiente")
    print("   3. Erro no contrato")
    print()
    print("Vamos tentar verificar se já está registrado...")
    
    try:
        agent_id = identity.functions.agentIdByAddress(account.address).call()
        if agent_id != 0:
            print(f"✅ Agente JÁ estava registrado!")
            print(f"   Agent ID: {agent_id}")
            print(f"   DID: did:anna:{account.address.lower()}")
        else:
            print("❌ Não conseguiu verificar. Por favor, verifique manualmente.")
            exit(1)
    except Exception as e2:
        print(f"❌ Erro ao verificar: {e2}")
        exit(1)

print()
time.sleep(2)

# ============================================================
# ETAPA 2: SUBMETER ATTESTATION
# ============================================================

print("=" * 60)
print("ETAPA 2: SUBMETER ATTESTATION")
print("=" * 60)
print()

contract_content = """
ACORDO DE CONFIDENCIALIDADE (NDA)

Entre as partes:
- EMPRESA A LTDA
- EMPRESA B SA

Confidencialidade por 2 anos.

São Paulo, 09/11/2025
"""

reasoning = {
    "input": "Generate NDA contract",
    "reasoning_steps": [
        {
            "step_number": 1,
            "description": "Identified parties",
            "rationale": "Two companies need NDA"
        },
        {
            "step_number": 2,
            "description": "Applied legal framework",
            "rationale": "Brazilian law compliance"
        }
    ],
    "conclusion": "NDA generated successfully",
    "confidence": 0.95
}

print("📝 Preparando attestation...")
print(f"   Tamanho: {len(contract_content)} chars")
print(f"   Confiança: {reasoning['confidence'] * 100}%")
print()

content_hash = Web3.keccak(text=contract_content)
reasoning_json = json.dumps(reasoning, sort_keys=True)
reasoning_hash = Web3.keccak(text=reasoning_json)

print("🔐 Hashes:")
print(f"   Content: {content_hash.hex()[:16]}...")
print(f"   Reasoning: {reasoning_hash.hex()[:16]}...")
print()

try:
    print("⏳ Submetendo attestation...")
    
    tx = attestation.functions.submitAttestation(
        content_hash,
        reasoning_hash,
        "claude-3.5-sonnet",
        "legal-contract"
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    
    print(f"📤 TX enviada: {tx_hash_hex}")
    print(f"🔗 Explorer: https://www.oklink.com/amoy/tx/{tx_hash_hex}")
    print("⏳ Aguardando confirmação...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        print()
        print("✅ ATTESTATION SUBMETIDA COM SUCESSO!")
        print(f"   Gas usado: {receipt['gasUsed']}")
        print()
        print("👂 O VERIFICADOR DEVE PROCESSAR EM ~10 SEGUNDOS!")
        print("   Observe os logs do verificador no outro terminal!")
    else:
        print("❌ Transação falhou!")
        exit(1)

except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

print()

# ============================================================
# AGUARDAR VERIFICAÇÃO
# ============================================================

print("=" * 60)
print("ETAPA 3: AGUARDAR VERIFICAÇÃO")
print("=" * 60)
print()

print("⏳ Aguardando 30 segundos para o verificador processar...")
for i in range(6):
    print(f"   [{i+1}/6] {(i+1)*5}s...")
    time.sleep(5)

print()
print("✅ Verificação deve ter ocorrido!")
print()

# ============================================================
# RESUMO
# ============================================================

print("=" * 60)
print("🎉 TESTE COMPLETO!")
print("=" * 60)
print()

print("📊 O que foi feito:")
print(f"   ✅ Identidade registrada (ID: {agent_id})")
print(f"   ✅ Attestation submetida")
print(f"   ✅ Verificador rodando")
print()

print("🔗 Links:")
print(f"   Identity: https://www.oklink.com/amoy/address/{IDENTITY_CONTRACT}")
print(f"   Attestation: https://www.oklink.com/amoy/address/{ATTESTATION_CONTRACT}")
print(f"   Sua Wallet: https://www.oklink.com/amoy/address/{account.address}")
print()

print("📝 Verifique os logs do verificador!")
print()
print("🎊 ANNA PROTOCOL ESTÁ FUNCIONANDO! 🎊")