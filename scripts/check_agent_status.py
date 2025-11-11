"""
Script simples para verificar status do agente
"""

from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

load_dotenv()

POLYGON_AMOY_RPC = "https://rpc-amoy.polygon.technology/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY") or os.getenv("VERIFIER_PRIVATE_KEY")
IDENTITY_CONTRACT = "0x8b9b5D3f698BE53Ae98162f6e013Bc9214bc7AF0"

w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC))
account = Account.from_key(PRIVATE_KEY)

identity_abi = [
    {
        "inputs": [{"name": "agentAddress", "type": "address"}],
        "name": "agentIdByAddress",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

identity = w3.eth.contract(
    address=Web3.to_checksum_address(IDENTITY_CONTRACT),
    abi=identity_abi
)

print("🔍 Verificando status do agente...")
print(f"   Wallet: {account.address}")
print()

try:
    agent_id = identity.functions.agentIdByAddress(account.address).call()
    
    if agent_id == 0:
        print("❌ Agente NÃO está registrado")
        print("   Você pode registrar agora")
    else:
        print("✅ Agente JÁ ESTÁ REGISTRADO!")
        print(f"   Agent ID: {agent_id}")
        print(f"   DID: did:anna:{account.address.lower()}")
        print()
        print("🎉 Você pode pular a etapa de registro!")
        print("   Vá direto para submeter attestations!")
        
except Exception as e:
    print(f"❌ Erro ao verificar: {e}")