# Test 10: MMC entre Dois Números

## Descrição
Programa que calcula o Mínimo Múltiplo Comum (MMC) entre dois números usando o algoritmo de Euclides para calcular o MDC (Máximo Divisor Comum).

## Entrada
- a: primeiro número inteiro positivo
- b: segundo número inteiro positivo

## Saída Esperada
- **-1**: se a ≤ 0 ou b ≤ 0 (entrada inválida)
- **MMC(a, b)**: o mínimo múltiplo comum entre a e b

## Exemplos
- Input: 5, 0 → Output: -1
- Input: 12, 45 → Output: 180

## Algoritmo
1. Se a ≤ 0, retorna -1
2. Se b ≤ 0, retorna -1
3. p = a * b (produto dos números)
4. Algoritmo de Euclides:
   - r = a % b
   - a = b
   - b = r
   - Repete enquanto r ≠ 0
5. Quando r = 0, a contém o MDC
6. MMC = p / MDC = p / a

## Testa
- Múltiplos inputs
- Validação de entrada
- Algoritmo de Euclides (loop com condição)
- Operações aritméticas: *, /, %
- Reatribuição de variáveis
