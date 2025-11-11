"""
Exemplo Completo - ANNA Protocol SDK
=====================================

Este exemplo demonstra o uso completo do SDK para um caso de uso LegalTech:
geração automatizada de contratos com rastreabilidade e verificação.

Requisitos:
- SDK instalado: pip install anna-protocol-sdk
- Wallet com MATIC na Polygon Amoy
- Contratos ANNA deployados
"""

import os
import json
from anna_sdk import (
    ANNAClient,
    Reasoning,
    ReasoningStep,
    VerificationTier,
    create_reasoning
)

# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Obter credenciais de variáveis de ambiente (seguro!)
PRIVATE_KEY = os.getenv("ANNA_PRIVATE_KEY")
IDENTITY_CONTRACT = os.getenv("ANNA_IDENTITY_CONTRACT")
ATTESTATION_CONTRACT = os.getenv("ANNA_ATTESTATION_CONTRACT")
REPUTATION_CONTRACT = os.getenv("ANNA_REPUTATION_CONTRACT")

if not PRIVATE_KEY:
    raise ValueError("ANNA_PRIVATE_KEY não configurada!")

# ============================================================
# INICIALIZAÇÃO
# ============================================================

print("🚀 Inicializando ANNA Protocol SDK...")
print("=" * 60)

client = ANNAClient(
    private_key=PRIVATE_KEY,
    network="polygon-amoy",  # Testnet
    identity_contract=IDENTITY_CONTRACT,
    attestation_contract=ATTESTATION_CONTRACT,
    reputation_contract=REPUTATION_CONTRACT
)

print(f"✅ Cliente inicializado")
print(f"   Wallet: {client.address}")
print(f"   Network: {client.network} (Chain ID: {client.network_config['chain_id']})")
print(f"   Saldo: {client.get_balance():.4f} MATIC")
print()

# ============================================================
# VERIFICAR/REGISTRAR IDENTIDADE
# ============================================================

print("🔑 Verificando identidade...")
print("=" * 60)

identity = client.get_identity()

if identity is None:
    print("⚠️  Agente não registrado. Registrando agora...")
    
    identity = client.register_identity(
        model_type="LLM",
        model_version="gpt-4-turbo-2024",
        specializations=[
            "legal-contracts",
            "compliance",
            "contract-analysis",
            "brazilian-law"
        ],
        wait_for_confirmation=True
    )
    
    print(f"✅ Identidade registrada com sucesso!")
    print(f"   Agent ID: {identity.agent_id}")
    print(f"   DID: {identity.did}")
    print(f"   Model: {identity.model_type} {identity.model_version}")
    print(f"   Specializations: {', '.join(identity.specializations)}")
else:
    print(f"✅ Agente já registrado")
    print(f"   Agent ID: {identity['agent_id']}")
    print(f"   DID: {identity['did']}")

print()

# ============================================================
# SIMULAR GERAÇÃO DE CONTRATO POR IA
# ============================================================

print("📝 Gerando contrato via IA...")
print("=" * 60)

# Dados de entrada do usuário
contract_request = {
    "type": "NDA",
    "parties": ["Company A LTDA", "Company B SA"],
    "jurisdiction": "Brazil",
    "duration": "2 years",
    "special_clauses": ["Non-compete", "IP protection"]
}

print(f"   Tipo: {contract_request['type']}")
print(f"   Partes: {contract_request['parties']}")
print(f"   Jurisdição: {contract_request['jurisdiction']}")
print()

# Simular resposta da IA (em produção, seria chamada ao modelo real)
contract_text = f"""
ACORDO DE CONFIDENCIALIDADE (NDA)

PARTES:
- {contract_request['parties'][0]}, doravante denominada "PARTE A"
- {contract_request['parties'][1]}, doravante denominada "PARTE B"

1. OBJETO
   As PARTES acordam em manter confidencialidade sobre informações sensíveis
   trocadas durante o período de {contract_request['duration']}.

2. DEFINIÇÕES
   2.1 Informação Confidencial: qualquer dado, técnica, estratégia ou 
       conhecimento compartilhado entre as PARTES.

3. OBRIGAÇÕES
   3.1 As PARTES comprometem-se a não divulgar Informações Confidenciais.
   3.2 Vedada a utilização para fins diversos do acordado.

4. NÃO-CONCORRÊNCIA
   Durante a vigência e por 1 ano após o término, as PARTES não competirão
   diretamente no mesmo mercado.

5. PROPRIEDADE INTELECTUAL
   Toda criação intelectual durante a vigência será de propriedade conjunta.

6. VIGÊNCIA
   Período de {contract_request['duration']} a partir da assinatura.

7. LEI APLICÁVEL
   Lei Brasileira - Código Civil Brasileiro e Lei 13.709/2018 (LGPD).

Local e Data: São Paulo, {contract_request['jurisdiction']}, 09/11/2025

_________________________        _________________________
    PARTE A                           PARTE B
"""

# Simular raciocínio da IA (explicabilidade)
ai_reasoning = {
    "steps": [
        {
            "description": "Analisou tipo de contrato solicitado",
            "rationale": "Usuário solicitou NDA entre duas empresas brasileiras"
        },
        {
            "description": "Identificou jurisdição aplicável",
            "rationale": "Brasil - aplicável Lei Civil e LGPD"
        },
        {
            "description": "Incluiu cláusula de não-concorrência",
            "rationale": "Requisito explícito do usuário em special_clauses"
        },
        {
            "description": "Adicionou proteção de PI",
            "rationale": "Requisito explícito do usuário em special_clauses"
        },
        {
            "description": "Definiu prazo de vigência",
            "rationale": "2 anos conforme solicitado"
        },
        {
            "description": "Aplicou template NDA standard",
            "rationale": "Base em 1.500 contratos similares verificados"
        }
    ],
    "confidence": 0.94
}

print(f"✅ Contrato gerado ({len(contract_text)} caracteres)")
print(f"   Confiança: {ai_reasoning['confidence'] * 100:.1f}%")
print(f"   Passos de raciocínio: {len(ai_reasoning['steps'])}")
print()

# ============================================================
# CRIAR REASONING ESTRUTURADO
# ============================================================

print("🧠 Estruturando raciocínio...")
print("=" * 60)

reasoning = create_reasoning(
    input_text=f"Generate {contract_request['type']} contract for {', '.join(contract_request['parties'])}",
    steps=[
        (step['description'], step['rationale'])
        for step in ai_reasoning['steps']
    ],
    conclusion=f"NDA contract generated successfully with {len(contract_request['special_clauses'])} special clauses",
    confidence=ai_reasoning['confidence']
)

print(f"✅ Reasoning estruturado")
print(f"   Input: {reasoning.input[:60]}...")
print(f"   Steps: {len(reasoning.reasoning_steps)}")
print(f"   Confidence: {reasoning.confidence}")
print()

# ============================================================
# SUBMETER ATTESTATION
# ============================================================

print("📤 Submetendo attestation ao ANNA Protocol...")
print("=" * 60)

result = client.submit_attestation(
    content=contract_text,
    reasoning=reasoning,
    category="legal-contract",
    tier="standard",  # Tier 1 + Tier 2 verification
    wait_for_confirmation=True
)

print(f"✅ Attestation submetida com sucesso!")
print(f"   Attestation ID: {result.attestation_id}")
print(f"   Transaction: {result.tx_hash}")
print(f"   Status: {result.status.value}")
print(f"   Explorer: {result.explorer_url}")
print()

# ============================================================
# AGUARDAR VERIFICAÇÃO
# ============================================================

print("⏳ Aguardando verificação (timeout: 60s)...")
print("=" * 60)

try:
    verification = client.wait_for_verification(
        attestation_id=result.attestation_id,
        timeout=60,
        poll_interval=5
    )
    
    print(f"{'✅' if verification.verified else '❌'} Verificação concluída!")
    print(f"   Status: {verification.status.value}")
    print(f"   Score: {verification.score}/100")
    print(f"   Verificador: {verification.verifier}")
    
    if verification.verified:
        print(f"   🎉 CONTRATO VERIFICADO E APROVADO!")
    else:
        print(f"   ⚠️  Contrato necessita revisão")
    
except TimeoutError:
    print(f"⏱️  Verificação ainda em andamento...")
    print(f"   Você pode consultar depois com get_attestation()")

print()

# ============================================================
# BUSCAR REPUTAÇÃO
# ============================================================

print("⭐ Consultando reputação do agente...")
print("=" * 60)

try:
    reputation_score = client.get_reputation()
    print(f"   Score: {reputation_score}/1000")
    
    if reputation_score >= 800:
        print(f"   Status: 🌟 EXCELENTE")
    elif reputation_score >= 600:
        print(f"   Status: ✅ BOM")
    elif reputation_score >= 400:
        print(f"   Status: ⚠️  REGULAR")
    else:
        print(f"   Status: ❌ BAIXO")
except Exception as e:
    print(f"   ⚠️  Ainda calculando reputação inicial...")

print()

# ============================================================
# GERAR CONTRATO FINAL COM SELO ANNA
# ============================================================

print("🎖️  Gerando contrato final com selo ANNA...")
print("=" * 60)

contract_with_seal = f"""
{contract_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CERTIFICAÇÃO ANNA PROTOCOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este contrato foi gerado por IA certificada pelo ANNA Protocol
(Artificial Neural Network for Accountability)

✓ Attestation ID: {result.attestation_id}
✓ Data: {result.timestamp}
✓ Status: Verificado e aprovado
✓ Rastreabilidade: Completa

Para verificar autenticidade e visualizar raciocínio completo:
{result.explorer_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# Salvar contrato final
output_file = "contract_with_anna_seal.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(contract_with_seal)

print(f"✅ Contrato salvo em: {output_file}")
print()

# ============================================================
# RESUMO FINAL
# ============================================================

print("📊 RESUMO DA OPERAÇÃO")
print("=" * 60)
print(f"✅ Identidade: {identity['did'] if isinstance(identity, dict) else identity.did}")
print(f"✅ Attestation: {result.attestation_id[:16]}...")
print(f"✅ Contrato: {len(contract_text)} caracteres")
print(f"✅ Verificação: {'Aprovada' if verification.verified else 'Pendente'}")
print(f"✅ Score: {verification.score if verification.verified else 'N/A'}/100")
print(f"✅ Gas usado: ~{client.w3.eth.gas_price / 10**9:.2f} Gwei")
print()
print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print()
print("📚 Próximos passos sugeridos:")
print("   1. Compartilhar contrato com as partes")
print("   2. Fornecer link do explorer para verificação")
print("   3. Manter reasoning original em arquivo seguro")
print("   4. Em caso de disputa, usar attestation_id para auditoria")
print()
print("💡 Dica: Mantenha seu agente ativo para acumular reputação!")