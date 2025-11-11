"""
Debug Script - Investigar falha no registro
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

print("🔍 DEBUG - Investigando falha no registro")
print("=" * 60)
print()

# ABI completo para o registerAgent
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

identity = w3.eth.contract(
    address=Web3.to_checksum_address(IDENTITY_CONTRACT),
    abi=identity_abi
)

print("📊 Informações da Wallet:")
print(f"   Endereço: {account.address}")
print(f"   Saldo: {w3.from_wei(w3.eth.get_balance(account.address), 'ether'):.4f} MATIC")
print(f"   Nonce: {w3.eth.get_transaction_count(account.address)}")
print()

print("📊 Informações do Contrato:")
print(f"   Endereço: {IDENTITY_CONTRACT}")
print(f"   Código existe: {len(w3.eth.get_code(Web3.to_checksum_address(IDENTITY_CONTRACT))) > 0}")
print()

# Verificar se já está registrado
agent_id = identity.functions.agentIdByAddress(account.address).call()
print(f"📊 Status do Agente:")
print(f"   Agent ID: {agent_id}")
print(f"   Registrado: {'Sim' if agent_id != 0 else 'Não'}")
print()

if agent_id != 0:
    print("✅ Agente já está registrado! Nada a fazer.")
    exit(0)

# Tentar estimar gas
print("🔍 Tentando estimar gas...")
try:
    gas_estimate = identity.functions.registerAgent(
        "LLM",
        "claude-3.5-sonnet",
        ["blockchain", "web3", "smart-contracts"]
    ).estimate_gas({'from': account.address})
    
    print(f"✅ Gas estimado: {gas_estimate}")
    print()
except Exception as e:
    print(f"❌ ERRO ao estimar gas!")
    print(f"   Mensagem: {str(e)}")
    print()
    print("💡 Isso indica que a transação vai falhar!")
    print()
    
    # Tentar descobrir o motivo
    if "execution reverted" in str(e).lower():
        print("🔍 Possíveis causas:")
        print("   1. Contrato tem um require() que está falhando")
        print("   2. Pode ter uma função onlyOwner ou similar")
        print("   3. Contrato pode estar pausado")
        print()
        
        # Tentar chamar direto para ver a mensagem de erro
        print("🔍 Tentando chamar função diretamente para ver erro...")
        try:
            result = identity.functions.registerAgent(
                "LLM",
                "claude-3.5-sonnet",
                ["blockchain", "web3", "smart-contracts"]
            ).call({'from': account.address})
            print(f"✅ Chamada funcionou: {result}")
        except Exception as e2:
            print(f"❌ Erro: {str(e2)}")
            
            # Extrair mensagem de revert
            error_msg = str(e2)
            if "revert" in error_msg.lower():
                print()
                print("🔍 MENSAGEM DE REVERT DETECTADA:")
                print(f"   {error_msg}")
    
    exit(1)

# Se chegou aqui, tentar fazer o registro
print("=" * 60)
print("⏳ TENTANDO REGISTRAR...")
print("=" * 60)
print()

try:
    tx = identity.functions.registerAgent(
        "LLM",
        "claude-3.5-sonnet",
        ["blockchain", "web3", "smart-contracts"]
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': int(gas_estimate * 1.2),  # 20% a mais de margem
        'gasPrice': w3.eth.gas_price
    })
    
    print(f"📝 Transação construída:")
    print(f"   Gas: {tx['gas']}")
    print(f"   Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
    print(f"   Custo estimado: {w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether'):.6f} MATIC")
    print()
    
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    
    print(f"📤 TX enviada: {tx_hash_hex}")
    print(f"🔗 https://www.oklink.com/amoy/tx/{tx_hash_hex}")
    print()
    print("⏳ Aguardando confirmação...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print()
    if receipt['status'] == 1:
        agent_id = identity.functions.agentIdByAddress(account.address).call()
        print("✅ SUCESSO!")
        print(f"   Agent ID: {agent_id}")
        print(f"   Gas usado: {receipt['gasUsed']}")
    else:
        print("❌ FALHOU!")
        print(f"   Status: {receipt['status']}")
        print()
        print("🔍 Detalhes do receipt:")
        print(f"   Block: {receipt['blockNumber']}")
        print(f"   Gas usado: {receipt['gasUsed']}")
        
except Exception as e:
    print(f"❌ Erro durante registro: {e}")