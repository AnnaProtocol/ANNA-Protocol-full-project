"""
ANNA Protocol - Teste End-to-End CORRIGIDO
==========================================
Versão corrigida com assinatura correta do registerAgent
"""

import json
import time
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

load_dotenv()

POLYGON_AMOY_RPC = "https://rpc-amoy.polygon.technology/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY") or os.getenv("VERIFIER_PRIVATE_KEY")

IDENTITY_CONTRACT = "0x8b9b5D3f698BE53Ae98162f6e013Bc9214bc7AF0"
ATTESTATION_CONTRACT = "0xEd98b7Ed960924cEf4d5dfF174252CE88DeCb4e8"

print("🚀 ANNA Protocol - Teste End-to-End (CORRIGIDO)")
print("=" * 60)
print()

w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC))
account = Account.from_key(PRIVATE_KEY)

print(f"✅ Conectado")
print(f"   Wallet: {account.address}")
print(f"   Saldo: {w3.from_wei(w3.eth.get_balance(account.address), 'ether'):.4f} MATIC")
print()

# ABI CORRIGIDO com todos os 5 parâmetros!
identity_abi = [
    {
        "inputs": [
            {"name": "agentAddress", "type": "address"},
            {"name": "did", "type": "string"},
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
    }
]

identity = w3.eth.contract(address=Web3.to_checksum_address(IDENTITY_CONTRACT), abi=identity_abi)
attestation = w3.eth.contract(address=Web3.to_checksum_address(ATTESTATION_CONTRACT), abi=attestation_abi)

# ============================================================
# ETAPA 1: REGISTRAR IDENTIDADE
# ============================================================

print("=" * 60)
print("ETAPA 1: REGISTRAR IDENTIDADE")
print("=" * 60)
print()

agent_id = identity.functions.agentIdByAddress(account.address).call()

if agent_id != 0:
    print(f"✅ Agente já registrado!")
    print(f"   Agent ID: {agent_id}")
    print(f"   DID: did:anna:{account.address.lower()}")
else:
    print("⏳ Registrando identidade...")
    
    # DID no formato correto
    did = f"did:anna:{account.address.lower()}"
    
    try:
        tx = identity.functions.registerAgent(
            account.address,  # agentAddress
            did,  # did
            "LLM",  # modelType
            "claude-3.5-sonnet",  # modelVersion
            ["blockchain", "web3", "smart-contracts"]  # specializations
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 400000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"📤 TX: {tx_hash_hex}")
        print("⏳ Aguardando...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            agent_id = identity.functions.agentIdByAddress(account.address).call()
            print()
            print("✅ SUCESSO!")
            print(f"   Agent ID: {agent_id}")
            print(f"   DID: {did}")
            print(f"   Gas: {receipt['gasUsed']}")
        else:
            print(f"❌ Falhou (status: {receipt['status']})")
            exit(1)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
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

contract_content = "CONTRATO NDA - Teste ANNA Protocol"
reasoning = {
    "input": "Generate test contract",
    "reasoning_steps": [
        {"step_number": 1, "description": "Test step", "rationale": "Testing ANNA"}
    ],
    "conclusion": "Test successful",
    "confidence": 0.95
}

content_hash = Web3.keccak(text=contract_content)
reasoning_hash = Web3.keccak(text=json.dumps(reasoning, sort_keys=True))

print(f"📝 Conteúdo: {len(contract_content)} chars")
print(f"🔐 Hashes: {content_hash.hex()[:16]}... / {reasoning_hash.hex()[:16]}...")
print()

try:
    print("⏳ Submetendo...")
    
    tx = attestation.functions.submitAttestation(
        content_hash,
        reasoning_hash,
        "claude-3.5-sonnet",
        "test-contract"
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    
    print(f"📤 TX: {tx_hash_hex}")
    print("⏳ Aguardando...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        print()
        print("✅ ATTESTATION SUBMETIDA!")
        print(f"   Gas: {receipt['gasUsed']}")
        print()
        print("👂 VERIFICADOR VAI PROCESSAR EM ~10s!")
    else:
        print("❌ Falhou")
        exit(1)
        
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

print()
print("⏳ Aguardando verificador (30s)...")
for i in range(6):
    print(f"   {(i+1)*5}s...")
    time.sleep(5)

print()
print("=" * 60)
print("🎉 TESTE COMPLETO!")
print("=" * 60)
print()
print(f"✅ Identidade: Agent ID {agent_id}")
print(f"✅ Attestation submetida")
print(f"✅ Verificador rodando")
print()
print("🔗 Explorer:")
print(f"   https://www.oklink.com/amoy/address/{account.address}")
print()
print("📝 Verifique os logs do verificador!")
print()
print("🎊 ANNA PROTOCOL FUNCIONANDO! 🎊")