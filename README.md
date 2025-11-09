# ANNA Protocol v2.0
## Artificial Neural Network for Accountability

**A Camada de Identidade e Reputação para Agentes Autônomos de IA**

---

[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-blue)](https://soliditylang.org/)
[![Hardhat](https://img.shields.io/badge/Hardhat-2.19-yellow)](https://hardhat.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Setup e Instalação](#-setup-e-instalação)
- [Deploy](#-deploy)
- [Uso](#-uso)
- [Testes](#-testes)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)

---

## 🎯 Visão Geral

O ANNA Protocol resolve a **"Trinca da Confiança Semântica"** - a lacuna entre geração de decisões por IA e sua execução em sistemas críticos.

### Problema

Quando uma IA gera um contrato jurídico, aprova um crédito ou emite um diagnóstico médico, como provar:
- ✅ **Autoria**: Qual modelo/agente gerou a decisão?
- ✅ **Integridade**: A decisão foi adulterada após geração?
- ✅ **Coerência**: O raciocínio é logicamente consistente?
- ✅ **Responsabilidade**: Quem responde por erros ou vieses?

### Solução

O ANNA Protocol estabelece:

1. **Identidade Descentralizada (DID)** para agentes de IA
2. **Attestations Criptográficas** de decisões e raciocínios
3. **Verificação de Consistência** através de oráculos especializados
4. **Reputação On-Chain** baseada em histórico auditável

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│  (LegalTech, FinTech, HealthTech, DAOs, Autonomous Agents)  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   REPUTATION ENGINE                         │
│  (Score Calculation, Historical Analysis, Risk Assessment)  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   VERIFICATION LAYER                        │
│  (Oracles, Consistency Checks, Validation Nodes)           │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   ATTESTATION LAYER                         │
│  (Smart Contracts, On-Chain Registry, Identity Management)  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   IDENTITY LAYER                            │
│  (DIDs, Key Management, Agent Wallets)                      │
└─────────────────────────────────────────────────────────────┘
```

### Contratos Principais

#### 1. **AnnaIdentity.sol**
- NFT Soulbound (não transferível)
- Registro de identidade de agentes
- Metadados: tipo de modelo, versão, especializações
- DID no formato: `did:anna:0x...`

#### 2. **AnnaAttestation.sol**
- Registro de decisões e raciocínios
- Hashes criptográficos de conteúdo
- Sistema de verificação multi-tier
- Eventos auditáveis

#### 3. **AnnaReputation.sol**
- Cálculo de score de reputação (0-1000)
- Baseado em volume, consistência, idade e penalidades
- Histórico completo de attestations
- Queries públicas de reputação

---

## 📁 Estrutura do Projeto

```
anna-protocol/
├── contracts/                  # Smart Contracts (Solidity)
│   ├── contracts/
│   │   ├── AnnaIdentity.sol
│   │   ├── AnnaAttestation.sol
│   │   └── AnnaReputation.sol
│   ├── scripts/
│   │   ├── deploy.js
│   │   └── deploy-continue.js
│   ├── test/
│   │   └── anna-protocol.test.js
│   ├── hardhat.config.js
│   └── package.json
│
├── verifier/                   # Verificador Python (Tier 1)
│   ├── verifier.py
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── sdk/                        # SDK Python (em desenvolvimento)
│   └── anna_sdk.py
│
├── scripts/                    # Scripts de interação
│   └── interact.py
│
├── docs/                       # Documentação
│   ├── ANNA_Protocol_Whitepaper_v2.0.pdf
│   └── architecture.md
│
└── README.md                   # Este arquivo
```

---

## 🚀 Setup e Instalação

### Pré-requisitos

- **Node.js** 20.x LTS
- **Python** 3.10+
- **Git**
- **Metamask** ou wallet compatível
- **MATIC** na Polygon Amoy Testnet

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/anna-protocol.git
cd anna-protocol
```

### 2. Setup dos Contratos

```bash
cd contracts
npm install
```

Criar `.env`:

```env
PRIVATE_KEY=0x...
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology/
POLYGONSCAN_API_KEY=...
```

### 3. Setup do Verificador

```bash
cd ../verifier
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Criar `.env`:

```env
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology/
VERIFIER_PRIVATE_KEY=0x...
ATTESTATION_CONTRACT_ADDRESS=0x...
```

---

## 🎯 Deploy

### Compilar Contratos

```bash
cd contracts
npx hardhat compile
```

### Deploy na Testnet (Polygon Amoy)

```bash
npx hardhat run scripts/deploy.js --network polygonAmoy
```

Isso irá:
1. ✅ Deployar AnnaIdentity
2. ✅ Deployar AnnaAttestation (vinculado ao Identity)
3. ✅ Deployar AnnaReputation (vinculado ao Attestation)
4. ✅ Salvar endereços em `deployed-addresses.json`

### Verificar no Explorer

Os endereços serão salvos em `contracts/deployed-addresses.json`.

Verifique no Polygonscan:
```
https://amoy.polygonscan.com/address/{contract_address}
```

---

## 📖 Uso

### Registrar um Agente

```python
from anna_sdk import ANNAClient

client = ANNAClient(
    private_key="0x...",
    rpc_url="https://rpc-amoy.polygon.technology/",
    contracts={
        'identity': '0x...',
        'attestation': '0x...'
    }
)

# Registrar identidade
did = client.register_identity(
    model_type="LLM",
    model_version="gpt-4-turbo",
    specializations=["legal-contracts"]
)

print(f"DID: {did}")
```

### Criar Attestation

```python
# Gerar decisão com sua IA
decision = your_ai_model.generate(prompt)
reasoning = {
    "input": "Generate NDA contract",
    "reasoning_steps": [
        {
            "step_number": 1,
            "description": "Identified parties",
            "rationale": "Required for contract"
        }
    ],
    "conclusion": "NDA generated",
    "confidence": 0.95
}

# Registrar no ANNA
attestation_id = client.attest(
    content=decision,
    reasoning=reasoning,
    category="legal-contract"
)

print(f"Attestation ID: {attestation_id}")
```

### Rodar Verificador

```bash
cd verifier
python verifier.py
```

O verificador ficará escutando eventos e verificando automaticamente.

### Scripts de Teste

```bash
cd scripts
python interact.py
```

Menu interativo para:
- Registrar agente
- Submeter attestation
- Verificar reputação
- Autorizar verificador

---

## 🧪 Testes

### Testes Locais (Hardhat)

```bash
cd contracts
npx hardhat test
```

⚠️ **Nota:** Testes locais podem ter problemas no Windows. Recomendamos testar direto na testnet.

### Testes na Testnet

Após deploy, use o `interact.py`:

```bash
cd scripts
python interact.py
```

Escolha "Teste completo" no menu.

---

## 🗺️ Roadmap

### ✅ Fase 1: MVP (Q4 2025)
- [x] Smart contracts desenvolvidos
- [x] Verificador Tier 1 implementado
- [x] Deploy em testnet
- [ ] 1 parceiro piloto
- [ ] 100 attestations registradas

### 📍 Fase 2: Validação (Q1-Q2 2026)
- [ ] Verificador Tier 2 (LLM-based)
- [ ] Marketplace de verificadores Tier 3
- [ ] Sistema de staking e slashing
- [ ] 10 empresas clientes
- [ ] SDK JavaScript

### 🔮 Fase 3: Scale (Q3-Q4 2026)
- [ ] Mainnet launch
- [ ] Token $ANNA
- [ ] DAO governance
- [ ] Zero-Knowledge Proofs
- [ ] 100 empresas
- [ ] $100k MRR

---

## 📊 Métricas Atuais

| Métrica | Valor |
|---------|-------|
| Versão do Protocolo | 2.0 (Tier 1.1) |
| Contratos Deployados | 3 |
| Verificador | Tier 1.1 (7 checks) |
| Agentes Registrados | 0 |
| Attestations | 0 |
| Verificadores Ativos | 0 |
| Network | Polygon Amoy (testnet) |

### ✨ Novidades Tier 1.1 (Nov 2025)

- ✅ Hash SHA256 de reasoning (integridade off-chain)
- ✅ Modo dry-run (testes sem gas)
- ✅ Logging estruturado JSON (dashboard-ready)
- ✅ 7 checks de validação (era 6)
- ✅ CLI arguments customizáveis

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

### Guidelines

- Escreva testes para novas funcionalidades
- Siga os padrões de código (Solidity Style Guide)
- Documente mudanças no README
- Use commits semânticos

---

## 🔐 Segurança

### Auditorias

- ⏳ **Audit Pendente** - Planejada para Q1 2026
- ✅ Contratos baseados em OpenZeppelin (auditados)
- ✅ Testes unitários implementados

### Reportar Vulnerabilidades

Se encontrar uma vulnerabilidade de segurança:

1. **NÃO** abra uma issue pública
2. Envie email para: security@annaprotocol.io
3. Aguarde resposta em até 48h
4. Bug bounty disponível (após mainnet)

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🌐 Links

- **Website:** [Website](https://https://annaprotocol.github.io/anna-protocol/)
- **Whitepaper:** [PDF](docs/ANNA_Protocol_Whitepaper_v2.0.pdf)
- **Twitter:** [@ANNA_Protocol](https://twitter.com/ANNA_Protocol)
- **Discord:** [em breve]
- **Documentation:** [docs.annaprotocol.io](https://docs.annaprotocol.io)

---

## 👥 Time

**Fundador:**  
Antonio Rufino - [LinkedIn](https://linkedin.com/in/antoniorufino) | [Twitter](https://twitter.com/antoniorufino)

**Colaboradores:**  
Veja todos os [contribuidores](https://github.com/anna-protocol/contributors)

---

## 💬 Suporte

Precisa de ajuda?

- 📧 Email: hello@annaprotocol.io
- 💬 Discord: [servidor](https://discord.gg/anna)
- 🐦 Twitter: [@ANNA_Protocol](https://twitter.com/ANNA_Protocol)
- 📚 Docs: [docs.annaprotocol.io](https://docs.annaprotocol.io)

---

## 🙏 Agradecimentos

- OpenZeppelin pela biblioteca de contratos
- Hardhat pela infraestrutura de desenvolvimento
- Polygon pela testnet rápida e confiável
- Comunidade Ethereum por todo o suporte

---

<div align="center">

**"A inteligência artificial cria. O ANNA garante que possamos confiar."**

Made with ❤️ by the ANNA Protocol team

[Website](https://https://annaprotocol.github.io/anna-protocol/) • [Twitter](https://twitter.com/ANNA_Protocol) • [Discord](https://discord.gg/anna)

</div>