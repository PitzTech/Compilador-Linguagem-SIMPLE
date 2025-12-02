# Test 06: Números Perfeitos

## Descrição
Programa que verifica se um número é perfeito. Um número perfeito é aquele que é igual à soma de seus divisores próprios (excluindo ele mesmo).

## Entrada
- n: número inteiro

## Saída Esperada
- **-1**: se n < 2 (entrada inválida)
- **1**: se n é um número perfeito
- **0**: se n não é um número perfeito

## Exemplos
- Input: 1 → Output: -1
- Input: 6 → Output: 1 (6 = 1 + 2 + 3)
- Input: 12 → Output: 0

## Algoritmo
1. Se n < 2, retorna -1
2. Inicializa i = 2 e r = 1 (soma dos divisores)
3. Para cada i de 2 até n-1:
   - Se n % i == 0, adiciona i a r
4. Se r == n, é perfeito (retorna 1)
5. Caso contrário, não é perfeito (retorna 0)

## Testa
- Loops com modificação de variáveis
- Operador módulo (%)
- Múltiplas comparações
- Acumulação de valores
