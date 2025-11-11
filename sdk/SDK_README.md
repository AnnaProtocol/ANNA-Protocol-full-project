# ANNA Protocol SDK - Python

SDK oficial em Python para interagir com o ANNA Protocol (Artificial Neural Network for Accountability).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Visão Geral

O ANNA Protocol SDK permite que desenvolvedores integrem facilmente seus agentes de IA ao protocolo, fornecendo:

- ✅ **Identidade Descentralizada** - Registro de identidade on-chain para agentes de IA
- ✅ **Attestations Verificáveis** - Registro de decisões com raciocínio auditável
- ✅ **Reputação On-Chain** - Score de confiabilidade baseado em verificações
- ✅ **Interface Simples** - API pythonic e fácil de usar

## 📦 Instalação

```bash
pip install anna-protocol-sdk
```

Ou instalar do fonte:

```bash
git clone https://github.com/anna-protocol/sdk-python
cd sdk-python
pip install -e .
```

## 🚀 Início Rápido

### 1. Importar e Inicializar

```python
from anna_sdk import ANNAClient, Reasoning, ReasoningStep

# Inicializar cliente
client = ANNAClient(
    private_key="0x...",  # Sua chave privada
    network="polygon-amoy",  # ou "polygon-mainnet"
    identity_contract="0x...",
    attestation_contract="0x...",
    reputation_contract="0x..."
)
```

### 2. Registrar Identidade (primeira vez)

```python
# Registrar agente no protocolo
identity = client.register_identity(
    model_type="LLM",
    model_version="gpt-4-turbo",
    specializations=["legal", "contracts", "compliance"]
)

print(f"✅ Agente registrado!")
print(f"   DID: {identity.did}")
print(f"   Agent ID: {identity.agent_id}")
```

### 3. Submeter Attestation

```python
# Criar reasoning estruturado
reasoning = Reasoning(
    input="Generate NDA contract for Company A and B",
    reasoning_steps=[
        ReasoningStep(
            step_number=1,
            description="Identified parties and jurisdiction",
            rationale="Parties: Company A and B, Jurisdiction: Brazil"
        ),
        ReasoningStep(
            step_number=2,
            description="Applied legal framework",
            rationale="Used Brazilian Civil Code and LGPD"
        ),
        ReasoningStep(
            step_number=3,
            description="Generated confidentiality clauses",
            rationale="Standard NDA requirements with LGPD compliance"
        )
    ],
    conclusion="NDA contract generated successfully with legal compliance",
    confidence=0.95
)

# Conteúdo gerado pela IA
contract_text = """
ACORDO DE CONFIDENCIALIDADE (NDA)
Entre Company A e Company B...
[contrato completo aqui]
"""

# Submeter ao protocolo
result = client.submit_attestation(
    content=contract_text,
    reasoning=reasoning,
    category="legal-contract",
    tier="standard"  # basic, standard, ou premium
)

print(f"✅ Attestation submetida!")
print(f"   ID: {result.attestation_id}")
print(f"   TX: {result.tx_hash}")
print(f"   View: {result.explorer_url}")
```

### 4. Aguardar Verificação

```python
# Aguardar verificação (opcional)
verification = client.wait_for_verification(
    attestation_id=result.attestation_id,
    timeout=60  # segundos
)

if verification.verified:
    print(f"✅ Attestation VERIFICADA!")
    print(f"   Score: {verification.score}/100")
    print(f"   Verificador: {verification.verifier}")
else:
    print(f"❌ Attestation REJEITADA")
    print(f"   Score: {verification.score}/100")
```

### 5. Consultar Reputação

```python
# Buscar reputação do agente
score = client.get_reputation()
print(f"Reputation Score: {score}/1000")
```

## 📚 Exemplos Completos

### Exemplo 1: LegalTech - Geração de Contratos

```python
from anna_sdk import ANNAClient, create_reasoning

# Setup
client = ANNAClient(
    private_key="0x...",
    network="polygon-amoy",
    identity_contract="0x...",
    attestation_contract="0x..."
)

# Função que sua IA usa para gerar contratos
def generate_contract(parties, contract_type, jurisdiction):
    # Seu código de IA aqui
    contract = your_ai_model.generate(...)
    reasoning_data = your_ai_model.explain_reasoning()
    return contract, reasoning_data

# Gerar contrato
contract, reasoning_data = generate_contract(
    parties=["Company A", "Company B"],
    contract_type="NDA",
    jurisdiction="Brazil"
)

# Criar reasoning estruturado
reasoning = create_reasoning(
    input_text=f"Generate {reasoning_data['type']} for {', '.join(reasoning_data['parties'])}",
    steps=[
        (step['description'], step['rationale'])
        for step in reasoning_data['steps']
    ],
    conclusion=reasoning_data['conclusion'],
    confidence=reasoning_data['confidence']
)

# Registrar no ANNA Protocol
result = client.submit_attestation(
    content=contract,
    reasoning=reasoning,
    category="legal-contract",
    tier="premium"  # Verificação por advogados
)

# Adicionar selo ANNA ao contrato
contract_with_seal = f"""
{contract}

---
CERTIFICADO ANNA PROTOCOL
Attestation ID: {result.attestation_id}
Verificar autenticidade em: {result.explorer_url}
"""

# Entregar ao cliente
return contract_with_seal
```

### Exemplo 2: FinTech - Decisão de Crédito

```python
from anna_sdk import ANNAClient, Reasoning, ReasoningStep

client = ANNAClient(
    private_key="0x...",
    network="polygon-mainnet",  # PRODUÇÃO
    attestation_contract="0x..."
)

# Análise de crédito pela IA
applicant_data = {
    "income": 5000,
    "credit_score": 750,
    "debt_ratio": 0.3
}

# IA decide
ai_decision = credit_ai_model.evaluate(applicant_data)

# Criar reasoning estruturado (para explicabilidade LGPD/GDPR)
reasoning = Reasoning(
    input=f"Evaluate credit application for applicant #{applicant_data['id']}",
    reasoning_steps=[
        ReasoningStep(1, "Analyzed income", f"Income: R$ {applicant_data['income']}/month (above minimum threshold)"),
        ReasoningStep(2, "Evaluated credit score", f"Score: {applicant_data['credit_score']} (good standing)"),
        ReasoningStep(3, "Calculated debt ratio", f"Ratio: {applicant_data['debt_ratio']} (within acceptable range)"),
        ReasoningStep(4, "Applied risk model", "Risk level: Low (score > 700 and ratio < 0.4)")
    ],
    conclusion=f"Credit {'APPROVED' if ai_decision['approved'] else 'DENIED'} - Risk: {ai_decision['risk_level']}",
    confidence=ai_decision['confidence']
)

# Registrar decisão no blockchain
result = client.submit_attestation(
    content=json.dumps(ai_decision),
    reasoning=reasoning,
    category="credit-decision",
    tier="standard"
)

# Fornecer comprovante auditável ao cliente
print(f"""
Sua solicitação foi processada.

Decisão: {ai_decision['status']}
Attestation: {result.attestation_id}

Para mais detalhes ou contestação, acesse:
{result.explorer_url}
""")
```

### Exemplo 3: HealthTech - Diagnóstico Assistido

```python
from anna_sdk import ANNAClient, create_reasoning

client = ANNAClient(
    private_key="0x...",
    network="polygon-mainnet",
    attestation_contract="0x..."
)

# IA analisa exame médico
patient_exam = load_medical_image("xray.png")
diagnosis = medical_ai.analyze(patient_exam)

# Criar reasoning explicável
reasoning = create_reasoning(
    input_text=f"Analyze chest X-ray for patient #{patient_id}",
    steps=[
        ("Image preprocessing", "Applied normalization and noise reduction"),
        ("Feature extraction", "Detected 3 regions of interest"),
        ("Pattern matching", "Compared with 10,000 reference images"),
        ("Consultation with knowledge base", "Cross-referenced with medical literature"),
        ("Confidence calculation", "High confidence based on clear markers")
    ],
    conclusion=diagnosis['result'],
    confidence=diagnosis['confidence']
)

# Registrar no ANNA (para auditoria médica)
result = client.submit_attestation(
    content=json.dumps(diagnosis),
    reasoning=reasoning,
    category="medical-diagnosis",
    tier="premium"  # Requer validação por médico especialista
)

# Aguardar validação de especialista
verification = client.wait_for_verification(result.attestation_id, timeout=300)

if verification.verified and verification.score >= 80:
    print(f"✅ Diagnóstico validado por especialista")
    print(f"   Prosseguir com tratamento recomendado")
else:
    print(f"⚠️ Diagnóstico requer revisão adicional")
    print(f"   Encaminhar para junta médica")
```

## 🔧 API Reference

### `ANNAClient`

#### Inicialização

```python
ANNAClient(
    private_key: str,
    network: str = "polygon-amoy",
    identity_contract: Optional[str] = None,
    attestation_contract: Optional[str] = None,
    reputation_contract: Optional[str] = None
)
```

#### Métodos

- `register_identity()` - Registra identidade do agente
- `submit_attestation()` - Submete nova attestation
- `get_attestation()` - Busca attestation por ID
- `wait_for_verification()` - Aguarda verificação
- `get_reputation()` - Consulta score de reputação
- `get_balance()` - Retorna saldo de MATIC
- `get_identity()` - Busca dados de identidade

### `Reasoning`

Estrutura de dados para raciocínio estruturado:

```python
@dataclass
class Reasoning:
    input: str
    reasoning_steps: List[ReasoningStep]
    conclusion: str
    confidence: float  # 0.0 - 1.0
```

### `ReasoningStep`

Cada passo do raciocínio:

```python
@dataclass
class ReasoningStep:
    step_number: int
    description: str
    rationale: str
```

### Helper Functions

- `create_reasoning()` - Cria objeto Reasoning facilmente
- `calculate_content_hash()` - Calcula hash Keccak256

## 🌐 Redes Suportadas

| Rede | Network ID | Chain ID | RPC |
|------|------------|----------|-----|
| Polygon Amoy (Testnet) | `polygon-amoy` | 80002 | `https://rpc-amoy.polygon.technology/` |
| Polygon Mainnet | `polygon-mainnet` | 137 | `https://polygon-rpc.com` |

## 🧪 Testes

```bash
# Instalar dependências de dev
pip install -e ".[dev]"

# Rodar testes
pytest tests/

# Com coverage
pytest --cov=anna_sdk tests/
```

## 📝 Requisitos

- Python 3.10+
- web3.py >= 6.0.0
- eth-account >= 0.10.0

## 🔒 Segurança

⚠️ **NUNCA** compartilhe sua chave privada ou commit ela em repositórios!

**Melhores práticas:**
- Use variáveis de ambiente para chaves privadas
- Para produção, use wallets de hardware ou KMS
- Teste sempre em testnet primeiro
- Mantenha backups seguros

```python
import os

# BOM: Ler de variável de ambiente
client = ANNAClient(
    private_key=os.getenv("ANNA_PRIVATE_KEY"),
    network="polygon-amoy"
)

# RUIM: Hardcoded
client = ANNAClient(
    private_key="0x123...",  # NÃO FAÇA ISSO!
    network="polygon-amoy"
)
```

## 📖 Documentação Completa

Para documentação completa, visite: [docs.annaprotocol.io](https://docs.annaprotocol.io)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie um branch para sua feature (`git checkout -b feature/amazing`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para o branch (`git push origin feature/amazing`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Discord**: [discord.gg/anna-protocol](https://discord.gg/anna-protocol)
- **Twitter**: [@ANNAProtocol](https://twitter.com/ANNA_Protocol)
- **Email**: dev@annaprotocol.io
- **Issues**: [GitHub Issues](https://github.com/anna-protocol/sdk-python/issues)

## 🎓 Recursos Adicionais

- [Whitepaper](https://github.com/anna-protocol/whitepaper)
- [Smart Contracts](https://github.com/anna-protocol/contracts)
- [Examples Repository](https://github.com/anna-protocol/examples)
- [Community Tutorials](https://docs.annaprotocol.io/tutorials)

---

**ANNA Protocol** - Artificial Neural Network for Accountability  
*Identidade e Reputação para Agentes Autônomos de IA*