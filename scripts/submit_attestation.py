"""
ANNA Protocol - Submeter Attestation
=====================================
Script simples para submeter attestations (sem registro)
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
ATTESTATION_CONTRACT = "0xEd98b7Ed960924cEf4d5dfF174252CE88DeCb4e8"

w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC))
account = Account.from_key(PRIVATE_KEY)

print("📝 ANNA Protocol - Submeter Attestation")
print("=" * 60)
print()

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

attestation = w3.eth.contract(
    address=Web3.to_checksum_address(ATTESTATION_CONTRACT),
    abi=attestation_abi
)

# Criar conteúdo de teste
import random
test_num = random.randint(1, 1000)

contract_content = f"CONTRATO DE TESTE #{test_num} - ANNA Protocol"
reasoning = {
    "input": f"Generate test contract #{test_num}",
    "reasoning_steps": [
        {
            "step_number": 1,
            "description": f"Created test contract #{test_num}",
            "rationale": "Testing ANNA Protocol verification"
        },
        {
            "step_number": 2,
            "description": "Applied test framework",
            "rationale": "Using standard test template"
        }
    ],
    "conclusion": "Test contract generated successfully",
    "confidence": 0.95
}

content_hash = Web3.keccak(text=contract_content)
reasoning_hash = Web3.keccak(text=json.dumps(reasoning, sort_keys=True))

print(f"📝 Teste #{test_num}")
print(f"   Conteúdo: {len(contract_content)} chars")
print(f"   Confiança: 95%")
print()

try:
    print("⏳ Submetendo attestation...")
    
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
    print("⏳ Aguardando confirmação...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        print()
        print("✅ ATTESTATION SUBMETIDA!")
        print(f"   Gas: {receipt['gasUsed']}")
        print(f"   Explorer: https://www.oklink.com/amoy/tx/{tx_hash_hex}")
        print()
        print("👂 Verificador vai processar em ~10 segundos!")
        print("   Aguarde e veja os logs do verificador...")
    else:
        print("❌ Falhou")
        
except Exception as e:
    print(f"❌ Erro: {e}")