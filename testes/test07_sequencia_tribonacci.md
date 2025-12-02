# Test 07: Sequência de Tribonacci

## Descrição
Programa que imprime a sequência de Tribonacci até o n-ésimo termo. A sequência de Tribonacci é definida por:
- F(0) = 0
- F(1) = 1
- F(2) = 1
- F(n) = F(n-1) + F(n-2) + F(n-3) para n ≥ 3

## Entrada
- n: número inteiro não negativo

## Saída Esperada
- **-1**: se n < 0 (entrada inválida)
- **Sequência**: imprime cada termo da sequência de 0 até n

## Exemplos
- Input: -5 → Output: -1
- Input: 6 → Output: 0 1 1 2 4 7 13

## Algoritmo
1. Se n < 0, imprime -1 e termina
2. Inicializa a = 0, b = 1, c = 1
3. Imprime a (primeiro termo)
4. Se n < 1, termina
5. Repete n vezes:
   - x = a + b
   - a = b
   - b = c
   - c = c + x
   - Imprime termo
6. Decrementa n e volta ao passo 5

## Testa
- Loops com contador decrescente
- Múltiplas variáveis temporárias
- Sequência matemática complexa
- Impressão em loop
