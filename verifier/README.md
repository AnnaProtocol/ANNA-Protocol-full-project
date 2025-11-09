# ANNA Protocol - Verificador Tier 1

Verificador automático para validar attestations de agentes de IA.

## 🎯 Funcionalidades

- ✅ Escuta eventos `AttestationSubmitted` on-chain
- ✅ Valida estrutura JSON do raciocínio
- ✅ Detecta padrões proibidos (jailbreaks, ataques)
- ✅ Verifica consistência lógica
- ✅ Submete resultado on-chain automaticamente
- ✅ Logging detalhado de todas operações

## 📋 Pré-requisitos

- Python 3.10+
- Ambiente virtual ativado
- MATIC na wallet do verificador
- Wallet autorizada no contrato (via `addVerifier`)

## 🚀 Setup

### 1. Ativar ambiente virtual

```cmd
cd C:\PROJETOS2\ANNA\verifier
venv\Scripts\activate
```

### 2. Instalar dependências

```cmd
pip install web3 eth-account python-dotenv jsonschema
```

### 3. Configurar .env

Copie o `.env.example` para `.env` e preencha:

```cmd
copy .env.example .env
```

Edite o `.env` com:
- Sua chave privada do verificador
- Endereço do contrato AnnaAttestation
- RPC do Polygon Amoy

### 4. Copiar ABI do contrato

Após deploy dos contratos, copie o ABI:

```cmd
copy ..\contracts\artifacts\contracts\AnnaAttestation.sol\AnnaAttestation.json attestation_abi.json
```

Ou extraia apenas o ABI manualmente e salve como `attestation_abi.json`.

## ▶️ Executar

### Modo Normal (escuta contínua)

```cmd
python verifier.py
```

O verificador ficará rodando e verificando automaticamente todas novas attestations.

### Modo Dry-Run (teste sem transações)

```cmd
python verifier.py --dry-run
```

Simula verificações sem enviar transações reais (não gasta gas). Ideal para:
- Testar configuração
- Debug de problemas
- Validar reasoning antes de produção

### Customizar Intervalo de Polling

```cmd
python verifier.py --poll-interval 5
```

Define intervalo em segundos (padrão: 10s).

### Parar o Verificador

Pressione `Ctrl+C` para parar gracefully.

## 📊 Checks Executados

O Verificador Tier 1 executa 7 verificações:

0. **Hash de Integridade** - Calcula SHA256 do reasoning para auditoria off-chain
1. **Estrutura JSON** - Valida schema do reasoning
2. **Campos Obrigatórios** - Checa input, steps, conclusion, confidence
3. **Padrões Proibidos** - Detecta jailbreaks e ataques
4. **Range de Confiança** - Valida confidence entre 0-1
5. **Consistência de Passos** - Mínimo 1 passo válido
6. **Tamanho Razoável** - Entre 100 bytes e 50KB (anti-spam)

**Score Mínimo:** 60/100 para aprovar (5 de 7 checks)

## 🔐 Segurança

### Autorização no Contrato

O verificador precisa ser autorizado pelo owner do contrato:

```javascript
// No Hardhat console ou script
await attestationContract.addVerifier("endereço_do_verificador");
```

### Chave Privada

⚠️ **NUNCA** commite o arquivo `.env` com sua chave privada!

O `.gitignore` já está configurado para ignorar `.env`.

## 📝 Logs

O verificador gera dois tipos de logs:

### 1. Console Logs (humano-legível)

Exemplo de saída:

```
2025-11-09 01:23:45 - INFO - ============================================================
2025-11-09 01:23:45 - INFO - 🤖 ANNA Verifier Tier 1 Iniciado
2025-11-09 01:23:45 - INFO - ============================================================
2025-11-09 01:23:45 - INFO - Verificador: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5
2025-11-09 01:23:45 - INFO - Network: 80002
2025-11-09 01:23:45 - INFO - Contrato: 0x1234...
2025-11-09 01:23:45 - INFO - Saldo: 0.5000 MATIC
2025-11-09 01:23:45 - INFO - ✅ Verificador AUTORIZADO
2025-11-09 01:23:45 - INFO - ============================================================
2025-11-09 01:23:45 - INFO - 
2025-11-09 01:23:45 - INFO - ============================================================
2025-11-09 01:23:45 - INFO - 👂 Escutando novos attestations...
2025-11-09 01:23:45 - INFO -    Intervalo de polling: 10s
2025-11-09 01:23:45 - INFO - ============================================================
```

Quando detecta uma nova attestation:

```
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 
🔔 NOVA ATTESTATION DETECTADA!
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 
   ID: 0xabc123...
   Agent: 0x789...
   Category: legal-contract
   Timestamp: 1699564800

   ⏳ Buscando reasoning do storage off-chain...
   📄 Reasoning obtido (542 bytes)

   🔍 Executando verificação Tier 1...
   ✅ Verificação PASSOU - Score: 95/100 (6/6 checks)

   📤 Submetendo verificação...
   ✅ Verificação submetida com sucesso!
```

### 2. Logs Estruturados (máquina-legível)

**Localização:** `logs/verifier.json.log`

**Formato:**
```json
{"timestamp":"2025-11-09T12:34:56","level":"INFO","message":"Verification completed"}
```

**Verificações Individuais:** `logs/verifications/{attestation_id}.json`

```json
{
  "timestamp": "2025-11-09T12:34:56.789",
  "attestation_id": "0xabc123...",
  "result": {
    "passed": true,
    "score": 93,
    "tx_hash": "0xdef456...",
    "status": "success"
  },
  "verifier": "0x742d35..."
}
```

**Uso:** Integração com dashboards (Grafana, Kibana, etc)

## 🔧 Troubleshooting

### Erro: "Not authorized verifier"

Solução: Execute no Hardhat:

```javascript
const attestation = await ethers.getContractAt("AnnaAttestation", "endereço");
await attestation.addVerifier("endereço_do_verificador");
```

### Erro: "Insufficient funds"

Solução: Adicione MATIC à wallet do verificador via faucet.

### Erro: "Connection refused"

Solução: Verifique se o RPC está correto no `.env`.

## 📚 Próximos Passos

Após rodar o verificador:

1. Teste submetendo uma attestation via SDK
2. Observe os logs de verificação
3. Verifique on-chain no explorer
4. Integre com storage off-chain (IPFS/Arweave)

## 🤝 Contribuindo

Este é um projeto open-source. Contribuições são bem-vindas!

## 📄 Licença

MIT

---

**ANNA Protocol** - Artificial Neural Network for Accountability  
Identidade e Reputação para Agentes Autônomos de IA