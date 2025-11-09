"""
ANNA Protocol - Scripts de Interação
Scripts para testar os contratos após deploy na testnet
"""

from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json
import os

load_dotenv()

class ANNAInteraction:
    """Classe para interagir com os contratos ANNA"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_AMOY_RPC')))
        self.account = Account.from_key(os.getenv('PRIVATE_KEY'))
        
        # Carregar endereços dos contratos
        with open('../contracts/deployed-addresses.json', 'r') as f:
            addresses = json.load(f)
        
        # Carregar ABIs
        with open('../contracts/artifacts/contracts/AnnaIdentity.sol/AnnaIdentity.json', 'r') as f:
            identity_artifact = json.load(f)
            self.identity_abi = identity_artifact['abi']
        
        with open('../contracts/artifacts/contracts/AnnaAttestation.sol/AnnaAttestation.json', 'r') as f:
            attestation_artifact = json.load(f)
            self.attestation_abi = attestation_artifact['abi']
        
        with open('../contracts/artifacts/contracts/AnnaReputation.sol/AnnaReputation.json', 'r') as f:
            reputation_artifact = json.load(f)
            self.reputation_abi = reputation_artifact['abi']
        
        # Criar instâncias dos contratos
        self.identity = self.w3.eth.contract(
            address=Web3.to_checksum_address(addresses['identity']),
            abi=self.identity_abi
        )
        
        self.attestation = self.w3.eth.contract(
            address=Web3.to_checksum_address(addresses['attestation']),
            abi=self.attestation_abi
        )
        
        self.reputation = self.w3.eth.contract(
            address=Web3.to_checksum_address(addresses['reputation']),
            abi=self.reputation_abi
        )
        
        print(f"✅ Conectado à network: {self.w3.eth.chain_id}")
        print(f"✅ Wallet: {self.account.address}")
        print(f"✅ Saldo: {self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether')} MATIC")
    
    def register_agent(
        self,
        model_type: str = "LLM",
        model_version: str = "gpt-4-turbo",
        specializations: list = None
    ):
        """Registra um novo agente de IA"""
        
        if specializations is None:
            specializations = ["legal-contracts", "compliance"]
        
        did = f"did:anna:{self.account.address}"
        
        print(f"\n📝 Registrando agente...")
        print(f"   DID: {did}")
        print(f"   Model: {model_type} {model_version}")
        print(f"   Specializations: {specializations}")
        
        tx = self.identity.functions.registerAgent(
            self.account.address,
            did,
            model_type,
            model_version,
            specializations
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"   ⏳ Aguardando confirmação...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            agent_id = self.identity.functions.agentIdByAddress(self.account.address).call()
            print(f"   ✅ Agente registrado com ID: {agent_id}")
            print(f"   🔗 TX: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
            return agent_id
        else:
            print(f"   ❌ Falha no registro")
            return None
    
    def submit_attestation(
        self,
        content: str,
        reasoning: dict,
        category: str = "legal-contract"
    ):
        """Submete uma nova attestation"""
        
        # Calcular hashes
        content_hash = Web3.keccak(text=content)
        reasoning_hash = Web3.keccak(text=json.dumps(reasoning))
        
        print(f"\n📤 Submetendo attestation...")
        print(f"   Content Hash: {content_hash.hex()[:16]}...")
        print(f"   Reasoning Hash: {reasoning_hash.hex()[:16]}...")
        print(f"   Category: {category}")
        
        tx = self.attestation.functions.submitAttestation(
            content_hash,
            reasoning_hash,
            "v1.0",
            category
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"   ⏳ Aguardando confirmação...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            # Extrair attestation ID dos logs
            logs = self.attestation.events.AttestationSubmitted().process_receipt(receipt)
            if logs:
                attestation_id = logs[0]['args']['attestationId'].hex()
                print(f"   ✅ Attestation submetida!")
                print(f"   🆔 ID: {attestation_id}")
                print(f"   🔗 TX: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
                return attestation_id
        
        print(f"   ❌ Falha na submissão")
        return None
    
    def check_reputation(self, agent_address: str = None):
        """Verifica reputação de um agente"""
        
        if agent_address is None:
            agent_address = self.account.address
        
        print(f"\n📊 Verificando reputação de {agent_address}...")
        
        score, total, verified, avg_score = self.reputation.functions.getFullReputation(
            agent_address
        ).call()
        
        print(f"\n   Reputation Score: {score}/1000")
        print(f"   Total Attestations: {total}")
        print(f"   Verified: {verified}")
        print(f"   Average Consistency: {avg_score}/100")
        
        return score
    
    def authorize_verifier(self, verifier_address: str):
        """Autoriza um verificador (apenas owner)"""
        
        print(f"\n🔐 Autorizando verificador {verifier_address}...")
        
        tx = self.attestation.functions.addVerifier(
            Web3.to_checksum_address(verifier_address)
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"   ⏳ Aguardando confirmação...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            print(f"   ✅ Verificador autorizado!")
            print(f"   🔗 TX: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
        else:
            print(f"   ❌ Falha na autorização")


def test_full_workflow():
    """Testa o fluxo completo do protocolo"""
    
    print("="*60)
    print("🧪 TESTE COMPLETO DO ANNA PROTOCOL")
    print("="*60)
    
    anna = ANNAInteraction()
    
    # 1. Registrar agente
    print("\n" + "="*60)
    print("PASSO 1: Registrar Agente")
    print("="*60)
    
    agent_id = anna.register_agent(
        model_type="LLM",
        model_version="gpt-4-turbo-2024",
        specializations=["legal-contracts", "compliance", "medical-analysis"]
    )
    
    if not agent_id:
        print("❌ Falha no registro. Abortando teste.")
        return
    
    # 2. Submeter attestation
    print("\n" + "="*60)
    print("PASSO 2: Submeter Attestation")
    print("="*60)
    
    content = """
    NON-DISCLOSURE AGREEMENT
    
    This Agreement is entered into as of November 9, 2025, by and between:
    Party A: TechCorp Inc.
    Party B: Innovation Labs Ltd.
    
    The parties agree to maintain confidentiality of all proprietary information...
    """
    
    reasoning = {
        "input": "Generate NDA between TechCorp and Innovation Labs",
        "reasoning_steps": [
            {
                "step_number": 1,
                "description": "Identified parties and jurisdiction",
                "rationale": "Both parties are corporations in Brazil, requiring compliance with Civil Code"
            },
            {
                "step_number": 2,
                "description": "Determined contract type as bilateral NDA",
                "rationale": "Both parties will share confidential information mutually"
            },
            {
                "step_number": 3,
                "description": "Included standard confidentiality clauses",
                "rationale": "Aligned with LGPD requirements for data protection"
            },
            {
                "step_number": 4,
                "description": "Added term duration and termination conditions",
                "rationale": "Standard 5-year term with mutual termination rights"
            }
        ],
        "conclusion": "NDA successfully generated compliant with Brazilian law and LGPD",
        "confidence": 0.94
    }
    
    attestation_id = anna.submit_attestation(content, reasoning, "legal-contract")
    
    if not attestation_id:
        print("❌ Falha na submissão. Abortando teste.")
        return
    
    # 3. Verificar reputação inicial
    print("\n" + "="*60)
    print("PASSO 3: Verificar Reputação")
    print("="*60)
    
    anna.check_reputation()
    
    print("\n" + "="*60)
    print("✅ TESTE COMPLETO CONCLUÍDO!")
    print("="*60)
    print("\n💡 Próximos passos:")
    print("   1. Rode o verificador Python para verificar a attestation")
    print("   2. Após verificação, cheque a reputação novamente")
    print("   3. Veja os dados no explorer: https://amoy.polygonscan.com")


def authorize_my_verifier():
    """Autoriza a wallet do verificador"""
    
    anna = ANNAInteraction()
    
    verifier_address = input("\n🔑 Digite o endereço da wallet do verificador: ")
    anna.authorize_verifier(verifier_address)


def check_my_reputation():
    """Verifica sua reputação atual"""
    
    anna = ANNAInteraction()
    anna.check_reputation()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ANNA PROTOCOL - Scripts de Interação")
    print("="*60)
    print("\n Escolha uma opção:")
    print("   1. Teste completo (registrar + attestation)")
    print("   2. Apenas registrar agente")
    print("   3. Apenas submeter attestation")
    print("   4. Verificar minha reputação")
    print("   5. Autorizar verificador")
    print("   0. Sair")
    
    choice = input("\n➤ Opção: ")
    
    if choice == "1":
        test_full_workflow()
    elif choice == "2":
        anna = ANNAInteraction()
        anna.register_agent()
    elif choice == "3":
        anna = ANNAInteraction()
        content = input("Digite o conteúdo: ")
        reasoning = {
            "input": content,
            "reasoning_steps": [{
                "step_number": 1,
                "description": "Generated content",
                "rationale": "User request"
            }],
            "conclusion": "Content generated",
            "confidence": 0.9
        }
        anna.submit_attestation(content, reasoning)
    elif choice == "4":
        check_my_reputation()
    elif choice == "5":
        authorize_my_verifier()
    else:
        print("👋 Até logo!")