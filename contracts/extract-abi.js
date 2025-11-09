const fs = require('fs');
const path = require('path');

// Caminho do arquivo compilado
const artifactPath = path.join(__dirname, 'artifacts', 'contracts', 'AnnaAttestation.sol', 'AnnaAttestation.json');
const outputPath = path.join(__dirname, '..', 'verifier', 'attestation_abi.json');

try {
    // Ler o arquivo compilado
    const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
    
    // Extrair apenas o ABI
    const abi = artifact.abi;
    
    // Salvar no diretório do verifier
    fs.writeFileSync(outputPath, JSON.stringify(abi, null, 2));
    
    console.log('✅ ABI extraído com sucesso!');
    console.log(`📁 Salvo em: ${outputPath}`);
    console.log(`📊 ${abi.length} funções/eventos no ABI`);
    
} catch (error) {
    console.error('❌ Erro ao extrair ABI:', error.message);
    console.error('');
    console.error('Certifique-se de que:');
    console.error('1. Os contratos foram compilados: npx hardhat compile');
    console.error('2. O arquivo existe em:', artifactPath);
}