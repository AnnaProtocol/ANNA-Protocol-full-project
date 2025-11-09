# ANNA Protocol - Guia Rápido de Comandos

Referência rápida de todos os comandos para trabalhar com o ANNA Protocol.

---

## 🎯 Setup Inicial

### Instalar Dependências

```bash
# Contratos
cd contracts
npm install

# Verificador
cd ../verifier
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 🔨 Desenvolvimento

### Compilar Contratos

```bash
cd contracts
npx hardhat compile
```

### Limpar e Recompilar

```bash
npx hardhat clean
npx hardhat compile
```

### Ver Tamanho dos Contratos

```bash
npx hardhat size-contracts
```

---

## 🧪 Testes

### Rodar Todos os Testes

```bash
npx hardhat test
```

### Rodar Teste Específico

```bash
npx hardhat test test/anna-protocol.test.js
```

### Testes com Coverage

```bash
npx hardhat coverage
```

### Testes com Gas Report

```bash
REPORT_GAS=true npx hardhat test
```

---

## 🚀 Deploy

### Deploy Local (Hardhat Network)

```bash
# Terminal 1 - Iniciar node local
npx hardhat node

# Terminal 2 - Deploy
npx hardhat run scripts/deploy.js --network localhost
```

### Deploy Testnet (Polygon Amoy)

```bash
npx hardhat run scripts/deploy.js --network polygonAmoy
```

### Deploy Continuado (se já deployou Identity)

```bash
npx hardhat run scripts/deploy-continue.js --network polygonAmoy
```

### Verificar Contratos no Polygonscan

```bash
npx hardhat verify --network polygonAmoy ENDERECO_DO_CONTRATO "ARG1" "ARG2"
```

---

## 💼 Hardhat Console

### Abrir Console Local

```bash
npx hardhat console
```

### Abrir Console na Testnet

```bash
npx hardhat console --network polygonAmoy
```

### Exemplos de Uso no Console

```javascript
// Conectar aos contratos
const identity = await ethers.getContractAt("AnnaIdentity", "0x...");
const attestation = await ethers.getContractAt("AnnaAttestation", "0x...");

// Ver total de agentes
const total = await identity.totalAgents();
console.log("Total agentes:", total.toString());

// Registrar agente
const tx = await identity.registerAgent(
    "0xSeuEndereco",
    "did:anna:0x...",
    "LLM",
    "gpt-4",
    ["legal"]
);
await tx.wait();

// Autorizar verificador
await attestation.addVerifier("0xEnderecoVerificador");
```

---

## 🐍 Verificador Python

### Ativar Ambiente Virtual

```bash
cd verifier
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Instalar Dependências

```bash
pip install web3 eth-account python-dotenv jsonschema
```

### Rodar Verificador

```bash
# Modo normal
python verifier.py

# Modo teste (dry-run) - sem gastar gas
python verifier.py --dry-run

# Customizar intervalo de polling
python verifier.py --poll-interval 5

# Combinar opções
python verifier.py --dry-run --poll-interval 15
```

### Ver Logs Estruturados

```bash
# Ver log JSON
type logs\verifier.json.log  # Windows
cat logs/verifier.json.log   # Linux/Mac

# Ver verificação específica
type logs\verifications\0xabc123.json
```

### Parar Verificador

```
Ctrl+C
```

---

## 📊 Scripts de Interação

### Rodar Script Interativo

```bash
cd scripts
python interact.py
```

### Opções do Menu

```
1. Teste completo (registrar + attestation)
2. Apenas registrar agente
3. Apenas submeter attestation
4. Verificar minha reputação
5. Autorizar verificador
0. Sair
```

---

## 🔍 Consultas

### Verificar Saldo

```bash
cd contracts
node check-balance.js
```

### Gerar Nova Wallet

```bash
node generate-wallet.js
```

### Ver Endereços Deployados

```bash
type deployed-addresses.json  # Windows
cat deployed-addresses.json   # Linux/Mac
```

---

## 📦 NPM Scripts Úteis

Adicione ao `package.json` da pasta `contracts`:

```json
{
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "deploy:local": "hardhat run scripts/deploy.js --network localhost",
    "deploy:amoy": "hardhat run scripts/deploy.js --network polygonAmoy",
    "node": "hardhat node",
    "clean": "hardhat clean",
    "size": "hardhat size-contracts"
  }
}
```

Uso:

```bash
npm run compile
npm run test
npm run deploy:amoy
```

---

## 🛠️ Troubleshooting

### Erro: "Nonce too low"

```bash
# Resetar nonce
npx hardhat clean
rm -rf cache artifacts
```

### Erro: "Insufficient funds"

```bash
# Verificar saldo
node check-balance.js

# Pegar mais MATIC
# https://faucet.polygon.technology/
```

### Erro: "Contract not deployed"

```bash
# Verificar endereços
type deployed-addresses.json

# Re-deploy se necessário
npx hardhat run scripts/deploy.js --network polygonAmoy
```

### Erro: "Invalid signature"

```bash
# Verificar se a private key está correta no .env
# Verificar se é o endereço correto
```

---

## 🔐 Segurança

### Gerar Nova Chave Privada

```javascript
// No Node.js
const crypto = require('crypto');
console.log('0x' + crypto.randomBytes(32).toString('hex'));
```

### Verificar Endereço da Chave

```javascript
const { ethers } = require('ethers');
const wallet = new ethers.Wallet('0xSuaChavePrivada');
console.log('Address:', wallet.address);
```

### Nunca Compartilhe

⚠️ **NUNCA** compartilhe:
- Private keys
- Mnemonic phrases
- Arquivo `.env`

✅ **OK para compartilhar**:
- Endereços públicos (0x...)
- Transaction hashes
- Contract addresses

---

## 📈 Monitoramento

### Ver Logs do Verificador

```bash
# Logs em tempo real
python verifier.py

# Salvar logs em arquivo
python verifier.py > verifier.log 2>&1
```

### Checar Status dos Contratos

```javascript
// No console do Hardhat
const identity = await ethers.getContractAt("AnnaIdentity", "0x...");

// Total de agentes
const totalAgents = await identity.totalAgents();
console.log("Agentes:", totalAgents.toString());

// Metadados de um agente
const metadata = await identity.getAgentMetadata(1);
console.log("DID:", metadata.did);
console.log("Type:", metadata.modelType);
console.log("Active:", metadata.isActive);
```

### Verificar Attestations

```javascript
const attestation = await ethers.getContractAt("AnnaAttestation", "0x...");

// Total de attestations de um agente
const count = await attestation.attestationCount("0xAgentAddress");
console.log("Attestations:", count.toString());

// Dados de uma attestation
const att = await attestation.getAttestation("0xAttestationId");
console.log("Status:", att.status);
console.log("Score:", att.consistencyScore);
```

---

## 🌐 Links Úteis

### Explorers

- **Polygon Amoy:** https://amoy.polygonscan.com/
- **Procurar TX:** https://amoy.polygonscan.com/tx/{TX_HASH}
- **Procurar Address:** https://amoy.polygonscan.com/address/{ADDRESS}

### Faucets

- **Polygon Amoy:** https://faucet.polygon.technology/

### RPCs

- **Polygon Amoy:** https://rpc-amoy.polygon.technology/
- **Alchemy:** https://polygon-amoy.g.alchemy.com/v2/YOUR-API-KEY

### Documentação

- **Hardhat:** https://hardhat.org/docs
- **OpenZeppelin:** https://docs.openzeppelin.com/contracts/
- **Web3.py:** https://web3py.readthedocs.io/
- **Ethers.js:** https://docs.ethers.org/

---

## 🎓 Workflows Comuns

### Workflow 1: Desenvolvimento Local

```bash
# 1. Iniciar node local
npx hardhat node

# 2. Deploy (terminal 2)
npx hardhat run scripts/deploy.js --network localhost

# 3. Rodar testes
npx hardhat test

# 4. Interagir via console
npx hardhat console
```

### Workflow 2: Deploy em Testnet

```bash
# 1. Compilar
npx hardhat compile

# 2. Verificar saldo
node check-balance.js

# 3. Deploy
npx hardhat run scripts/deploy.js --network polygonAmoy

# 4. Copiar endereços
type deployed-addresses.json

# 5. Configurar verificador
cd ../verifier
# Editar .env com endereços
python verifier.py

# 6. Testar
cd ../scripts
python interact.py
```

### Workflow 3: Adicionar Verificador

```bash
# 1. No console do Hardhat
npx hardhat console --network polygonAmoy

# 2. Conectar ao contrato
const attestation = await ethers.getContractAt("AnnaAttestation", "0x...");

# 3. Adicionar verificador
await attestation.addVerifier("0xEnderecoDoVerificador");

# 4. Verificar
const isAuthorized = await attestation.authorizedVerifiers("0xEnderecoDoVerificador");
console.log("Autorizado:", isAuthorized);
```

---

## 📝 Checklist de Deploy

Antes de deployar em produção:

- [ ] Contratos compilam sem warnings
- [ ] Todos os testes passam
- [ ] Documentação atualizada
- [ ] .env configurado corretamente
- [ ] Saldo suficiente para gas
- [ ] Endereços salvos em arquivo seguro
- [ ] Contratos verificados no explorer
- [ ] Verificador autorizado
- [ ] Teste completo executado
- [ ] Backups das chaves privadas

---

## 🆘 Comandos de Emergência

### Pausar Operações (TODO: implementar Pausable)

```javascript
// Futura funcionalidade
await contract.pause();
```

### Revogar Verificador

```javascript
const attestation = await ethers.getContractAt("AnnaAttestation", "0x...");
await attestation.removeVerifier("0xEnderecoMalicioso");
```

### Backup de Dados

```bash
# Exportar endereços
copy deployed-addresses.json backup_YYYY-MM-DD.json

# Exportar ABIs
copy artifacts\contracts\AnnaIdentity.sol\AnnaIdentity.json backup\
```

---

**Última atualização:** Novembro 2025  
**Versão do protocolo:** 2.0  
**Mantenedor:** Antonio Rufino

Para dúvidas: hello@annaprotocol.io