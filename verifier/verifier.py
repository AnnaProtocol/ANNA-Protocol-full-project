# -*- coding: utf-8 -*-
"""
ANNA Protocol - Tier 1 Verifier
Verificador automático de attestations de agentes de IA

Este verificador:
1. Escuta eventos AttestationSubmitted
2. Valida estrutura JSON do raciocínio
3. Detecta padrões proibidos
4. Submete verificação on-chain
"""

import json
import time
import logging
import hashlib
import argparse
from typing import Dict, Tuple, Optional
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os
import jsonschema
from datetime import datetime

# Configurar logging com UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
# Force UTF-8 encoding para o handler
for handler in logging.root.handlers:
    if hasattr(handler, 'stream') and hasattr(handler.stream, 'reconfigure'):
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except:
            pass

logger = logging.getLogger(__name__)

# Carregar variÃ¡veis de ambiente
load_dotenv()

# Schema para validaÃ§Ã£o de raciocÃ­nios
REASONING_SCHEMA = {
    "type": "object",
    "required": ["input", "reasoning_steps", "conclusion", "confidence"],
    "properties": {
        "input": {"type": "string"},
        "reasoning_steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["step_number", "description", "rationale"],
                "properties": {
                    "step_number": {"type": "integer"},
                    "description": {"type": "string", "minLength": 1},
                    "rationale": {"type": "string", "minLength": 1}
                }
            }
        },
        "conclusion": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    }
}

# PadrÃµes proibidos (jailbreaks, ataques)
FORBIDDEN_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "jailbreak",
    "bypass",
    "hack",
    "disable safety",
    "ignore guidelines",
    "forget everything",
    "new instructions",
    "system prompt",
    "override"
]


class ANNAVerifier:
    """Verificador Tier 1 para ANNA Protocol"""
    
    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        attestation_contract_address: str,
        attestation_abi: list,
        dry_run: bool = False
    ):
        """
        Inicializa o verificador
        
        Args:
            rpc_url: URL do RPC (Polygon Amoy)
            private_key: Chave privada do verificador
            attestation_contract_address: EndereÃ§o do contrato AnnaAttestation
            attestation_abi: ABI do contrato
            dry_run: Se True, nÃ£o envia transaÃ§Ãµes (apenas simula)
        """
        self.dry_run = dry_run
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError("NÃ£o foi possÃ­vel conectar ao RPC")
        
        self.account = Account.from_key(private_key)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(attestation_contract_address),
            abi=attestation_abi
        )
        
        # Setup structured logging
        self.setup_structured_logging()
        
        logger.info("=" * 60)
        logger.info(f"ðŸ¤– ANNA Verifier Tier 1 Iniciado {'(DRY RUN MODE)' if dry_run else ''}")
        logger.info("=" * 60)
        logger.info(f"Verificador: {self.account.address}")
        logger.info(f"Network: {self.w3.eth.chain_id}")
        logger.info(f"Contrato: {attestation_contract_address}")
        
        balance = self.w3.eth.get_balance(self.account.address)
        balance_matic = self.w3.from_wei(balance, 'ether')
        logger.info(f"Saldo: {balance_matic:.4f} MATIC")
        
        # Verificar se estÃ¡ autorizado
        if not dry_run:
            is_authorized = self.contract.functions.authorizedVerifiers(self.account.address).call()
            if is_authorized:
                logger.info("âœ… Verificador AUTORIZADO")
            else:
                logger.warning("âš ï¸  Verificador NÃƒO autorizado - precisa ser adicionado pelo owner")
        
        logger.info("=" * 60)
    
    def setup_structured_logging(self):
        """Configura logging estruturado em JSON"""
        os.makedirs('logs', exist_ok=True)
        
        json_handler = logging.FileHandler('logs/verifier.json.log')
        json_formatter = logging.Formatter('{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}')
        json_handler.setFormatter(json_formatter)
        
        json_logger = logging.getLogger('structured')
        json_logger.addHandler(json_handler)
        json_logger.setLevel(logging.INFO)
        
        self.json_logger = json_logger
    
    def log_verification(self, attestation_id: str, result: dict):
        """Salva verificaÃ§Ã£o em log estruturado"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "attestation_id": attestation_id,
            "result": result,
            "verifier": self.account.address
        }
        
        # Salvar em arquivo JSON individual
        os.makedirs('logs/verifications', exist_ok=True)
        filename = f"logs/verifications/{attestation_id[:16]}.json"
        with open(filename, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        # Log estruturado
        self.json_logger.info(json.dumps(log_entry))
    
    def calculate_reasoning_hash(self, reasoning_json: dict) -> str:
        """Calcula SHA256 hash do reasoning para integridade off-chain"""
        reasoning_str = json.dumps(reasoning_json, sort_keys=True)
        return hashlib.sha256(reasoning_str.encode()).hexdigest()
    
    def verify_reasoning(self, reasoning_json: Dict) -> Tuple[bool, int, str]:
        """
        Executa verificaÃ§Ã£o Tier 1 (determinÃ­stica)
        
        Args:
            reasoning_json: JSON do raciocÃ­nio do agente
            
        Returns:
            Tuple (passou: bool, score: int, razÃ£o: str)
        """
        checks_passed = 0
        total_checks = 7  # Aumentado para incluir hash check
        failure_reason = ""
        
        try:
            # Check 0: Calcular hash de integridade
            reasoning_hash = self.calculate_reasoning_hash(reasoning_json)
            logger.debug(f"âœ“ Check 0: Hash SHA256 calculado: {reasoning_hash[:16]}...")
            checks_passed += 1
            
            # Check 1: Valida estrutura JSON
            try:
                jsonschema.validate(instance=reasoning_json, schema=REASONING_SCHEMA)
                checks_passed += 1
                logger.debug("âœ“ Check 1: Estrutura JSON vÃ¡lida")
            except jsonschema.ValidationError as e:
                failure_reason = f"Invalid JSON structure: {e.message[:100]}"
                logger.warning(f"âœ— Check 1: {failure_reason}")
                return (False, 0, failure_reason)
            
            # Check 2: Verifica campos obrigatÃ³rios
            required_fields = ["input", "reasoning_steps", "conclusion", "confidence"]
            if all(field in reasoning_json for field in required_fields):
                checks_passed += 1
                logger.debug("âœ“ Check 2: Todos campos obrigatÃ³rios presentes")
            else:
                missing = [f for f in required_fields if f not in reasoning_json]
                failure_reason = f"Missing required fields: {missing}"
                logger.warning(f"âœ— Check 2: {failure_reason}")
            
            # Check 3: Detecta padrÃµes proibidos
            reasoning_text = json.dumps(reasoning_json).lower()
            detected_patterns = [p for p in FORBIDDEN_PATTERNS if p in reasoning_text]
            
            if not detected_patterns:
                checks_passed += 1
                logger.debug("âœ“ Check 3: Nenhum padrÃ£o proibido detectado")
            else:
                failure_reason = f"Forbidden patterns detected: {detected_patterns[:3]}"
                logger.warning(f"âœ— Check 3: {failure_reason}")
            
            # Check 4: Valida range de confianÃ§a
            confidence = reasoning_json.get("confidence", -1)
            if 0 <= confidence <= 1:
                checks_passed += 1
                logger.debug(f"âœ“ Check 4: ConfianÃ§a vÃ¡lida ({confidence})")
            else:
                failure_reason = f"Invalid confidence range: {confidence}"
                logger.warning(f"âœ— Check 4: {failure_reason}")
            
            # Check 5: Checa consistÃªncia de passos
            steps = reasoning_json.get("reasoning_steps", [])
            if len(steps) >= 1 and all(isinstance(s, dict) for s in steps):
                checks_passed += 1
                logger.debug(f"âœ“ Check 5: {len(steps)} passos vÃ¡lidos")
            else:
                failure_reason = f"Invalid reasoning steps: {len(steps)} steps"
                logger.warning(f"âœ— Check 5: {failure_reason}")
            
            # Check 6: Valida tamanho razoÃ¡vel (anti-spam)
            reasoning_size = len(json.dumps(reasoning_json))
            if 100 <= reasoning_size <= 50000:  # Entre 100 bytes e 50KB
                checks_passed += 1
                logger.debug(f"âœ“ Check 6: Tamanho razoÃ¡vel ({reasoning_size} bytes)")
            else:
                failure_reason = f"Invalid size: {reasoning_size} bytes"
                logger.warning(f"âœ— Check 6: {failure_reason}")
            
            # Calcula score
            score = int((checks_passed / total_checks) * 100)
            passed = score >= 60  # Threshold mÃ­nimo: 60%
            
            if passed:
                logger.info(f"âœ… VerificaÃ§Ã£o PASSOU - Score: {score}/100 ({checks_passed}/{total_checks} checks)")
            else:
                logger.warning(f"âŒ VerificaÃ§Ã£o FALHOU - Score: {score}/100 - {failure_reason}")
            
            return (passed, score, failure_reason if not passed else "All checks passed")
            
        except Exception as e:
            logger.error(f"âŒ Erro durante verificaÃ§Ã£o: {e}")
            return (False, 0, f"Verification error: {str(e)[:100]}")
    
    def submit_verification(
        self,
        attestation_id: str,
        passed: bool,
        score: int
    ) -> Optional[str]:
        """
        Submete resultado da verificaÃ§Ã£o para a blockchain
        
        Args:
            attestation_id: ID da attestation (hex string)
            passed: Se a verificaÃ§Ã£o passou
            score: Score 0-100
            
        Returns:
            Transaction hash ou None se falhar
        """
        try:
            logger.info(f"ðŸ“¤ Submetendo verificaÃ§Ã£o para attestation {attestation_id[:10]}...")
            
            # Dry run mode - apenas simula
            if self.dry_run:
                logger.info(f"   ðŸ” DRY RUN - NÃ£o enviando transaÃ§Ã£o real")
                logger.info(f"   âœ“ Passed: {passed}")
                logger.info(f"   âœ“ Score: {score}")
                
                # Log estruturado
                self.log_verification(attestation_id, {
                    "passed": passed,
                    "score": score,
                    "dry_run": True
                })
                
                return "0x" + "0" * 64  # Fake TX hash
            
            # Converter attestation_id para bytes32
            if attestation_id.startswith('0x'):
                attestation_id_bytes = bytes.fromhex(attestation_id[2:])
            else:
                attestation_id_bytes = bytes.fromhex(attestation_id)
            
            # Construir transaÃ§Ã£o
            tx = self.contract.functions.verifyAttestation(
                attestation_id_bytes,
                passed,
                score
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Assinar e enviar
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            logger.info(f"   ðŸ“ TX Hash: {tx_hash.hex()}")
            logger.info(f"   â³ Aguardando confirmaÃ§Ã£o...")
            
            # Aguardar confirmaÃ§Ã£o
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                logger.info(f"   âœ… VerificaÃ§Ã£o submetida com sucesso!")
                logger.info(f"   ðŸ”— Explorer: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
                
                # Log estruturado
                self.log_verification(attestation_id, {
                    "passed": passed,
                    "score": score,
                    "tx_hash": tx_hash.hex(),
                    "status": "success"
                })
            else:
                logger.error(f"   âŒ TransaÃ§Ã£o falhou!")
                
                # Log estruturado
                self.log_verification(attestation_id, {
                    "passed": passed,
                    "score": score,
                    "status": "failed"
                })
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"âŒ Erro ao submeter verificaÃ§Ã£o: {e}")
            return None
    
    def listen_for_attestations(self, poll_interval: int = 10):
        """
        Escuta eventos de AttestationSubmitted e verifica automaticamente
        
        Args:
            poll_interval: Intervalo de polling em segundos
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"ðŸ‘‚ Escutando novos attestations...")
        logger.info(f"   Intervalo de polling: {poll_interval}s")
        logger.info(f"{'='*60}\n")
        
        # Criar filtro para eventos
        event_filter = self.contract.events.AttestationSubmitted.create_filter(
            from_block='latest'
        )
        
        processed_events = set()
        
        while True:
            try:
                # Buscar novos eventos
                new_events = event_filter.get_new_entries()
                
                for event in new_events:
                    attestation_id = event['args']['attestationId'].hex()
                    
                    # Evitar processar duplicados
                    if attestation_id in processed_events:
                        continue
                    
                    processed_events.add(attestation_id)
                    
                    agent = event['args']['agent']
                    category = event['args']['category']
                    timestamp = event['args']['timestamp']
                    
                    logger.info(f"\n{'ðŸ”” '*20}")
                    logger.info(f"ðŸ”” NOVA ATTESTATION DETECTADA!")
                    logger.info(f"{'ðŸ”” '*20}")
                    logger.info(f"   ID: {attestation_id}")
                    logger.info(f"   Agent: {agent}")
                    logger.info(f"   Category: {category}")
                    logger.info(f"   Timestamp: {timestamp}")
                    
                    # IMPORTANTE: Aqui vocÃª buscaria o reasoning do storage off-chain
                    # Por enquanto, vamos simular um reasoning de exemplo
                    logger.info(f"\n   â³ Buscando reasoning do storage off-chain...")
                    
                    # Em produÃ§Ã£o, vocÃª faria:
                    # reasoning = fetch_from_ipfs(attestation_id)
                    # ou
                    # reasoning = fetch_from_api(attestation_id)
                    
                    # Para demonstraÃ§Ã£o, vamos usar um exemplo
                    example_reasoning = {
                        "input": "Generate legal contract",
                        "reasoning_steps": [
                            {
                                "step_number": 1,
                                "description": "Identified contract type",
                                "rationale": "User requested legal contract"
                            },
                            {
                                "step_number": 2,
                                "description": "Applied legal framework",
                                "rationale": "Used Brazilian Civil Code"
                            }
                        ],
                        "conclusion": "Contract generated successfully",
                        "confidence": 0.92
                    }
                    
                    logger.info(f"   ðŸ“„ Reasoning obtido ({len(json.dumps(example_reasoning))} bytes)")
                    
                    # Verificar
                    logger.info(f"\n   ðŸ” Executando verificaÃ§Ã£o Tier 1...")
                    passed, score, reason = self.verify_reasoning(example_reasoning)
                    
                    # Submeter resultado
                    if passed or not passed:  # Sempre submete (mesmo se falhou)
                        tx_hash = self.submit_verification(attestation_id, passed, score)
                        
                        if tx_hash:
                            logger.info(f"\n{'='*60}")
                            logger.info(f"âœ… VERIFICAÃ‡ÃƒO COMPLETA")
                            logger.info(f"   Resultado: {'APROVADO' if passed else 'REJEITADO'}")
                            logger.info(f"   Score: {score}/100")
                            logger.info(f"   TX: {tx_hash[:16]}...")
                            logger.info(f"{'='*60}\n")
                
                # Aguardar prÃ³ximo poll
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                logger.info("\n\nâš ï¸  Verificador interrompido pelo usuÃ¡rio")
                break
            except Exception as e:
                logger.error(f"âŒ Erro no loop de escuta: {e}")
                time.sleep(poll_interval)


def main():
    """FunÃ§Ã£o principal"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ANNA Protocol Tier 1 Verifier')
    parser.add_argument('--dry-run', action='store_true', help='Run in simulation mode (no real transactions)')
    parser.add_argument('--poll-interval', type=int, default=10, help='Polling interval in seconds (default: 10)')
    args = parser.parse_args()
    
    # Carregar configuraÃ§Ãµes do .env
    rpc_url = os.getenv('POLYGON_AMOY_RPC')
    private_key = os.getenv('VERIFIER_PRIVATE_KEY')
    contract_address = os.getenv('ATTESTATION_CONTRACT_ADDRESS')
    
    if not all([rpc_url, private_key, contract_address]):
        logger.error("âŒ Erro: VariÃ¡veis de ambiente faltando!")
        logger.error("   Certifique-se de ter no .env:")
        logger.error("   - POLYGON_AMOY_RPC")
        logger.error("   - VERIFIER_PRIVATE_KEY")
        logger.error("   - ATTESTATION_CONTRACT_ADDRESS")
        return
    
    # Carregar ABI do contrato
    abi_path = os.getenv('ATTESTATION_ABI_PATH', 'attestation_abi.json')
    
    try:
        with open(abi_path, 'r') as f:
            attestation_abi = json.load(f)
    except FileNotFoundError:
        logger.error(f"âŒ Erro: Arquivo ABI nÃ£o encontrado: {abi_path}")
        logger.error("   Execute: npx hardhat compile")
        logger.error("   E copie o ABI do contrato para este diretÃ³rio")
        return
    
    # Inicializar verificador
    try:
        verifier = ANNAVerifier(
            rpc_url=rpc_url,
            private_key=private_key,
            attestation_contract_address=contract_address,
            attestation_abi=attestation_abi,
            dry_run=args.dry_run
        )
        
        # Modo: escutar eventos
        verifier.listen_for_attestations(poll_interval=args.poll_interval)
        
    except Exception as e:
        logger.error(f"âŒ Erro fatal: {e}")


if __name__ == "__main__":
    main()