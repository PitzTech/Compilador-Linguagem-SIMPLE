# Test 11: Otimização - Constant Folding

## Descrição
Programa de teste para validar a otimização de constant folding (dobra de constantes). O programa realiza uma sequência de operações aritméticas simples que o compilador deve otimizar.

## Entrada
Nenhuma

## Saída Esperada
- 15
- 0
- 15
- 0
- 15

## Algoritmo
1. a = 0, b = 1, c = 3, d = 6, e = 10, f = 15 → imprime f (15)
2. g = 14, h = 12, i = 9, j = 5, k = 0 → imprime k (0)
3. l = 1, m = 3, n = 6, o = 10, p = 15 → imprime p (15)
4. q = 14, r = 12, s = 9, t = 5, u = 0 → imprime u (0)
5. v = 1, w = 3, x = 6, y = 10, z = 15 → imprime z (15)

## Otimizações Testadas
1. **Constant Folding**: Todas as expressões são constantes e devem ser calculadas em tempo de compilação
   - `let a = 0` → LOAD const0
   - `let b = a + 1` → LOAD const1 (se constant folding funcionar)
   - `let c = b + 2` → LOAD const3 (se constant folding funcionar)

2. **Constant Sharing**: Constantes repetidas devem compartilhar o mesmo endereço de memória
   - O valor 15 aparece 5 vezes, mas deve ocupar apenas 1 endereço
   - O valor 0 aparece 3 vezes, mas deve ocupar apenas 1 endereço

3. **Dead Code Elimination**: Variáveis que não são usadas depois podem não precisar de storage

## Expectativa de Otimização
- **Sem otimização**: ~62 palavras (26 variáveis + constantes)
- **Com otimização**: ~62 palavras (constant folding aplicado)
- **Economia**: Principalmente em constantes compartilhadas (10 constantes únicas ao invés de 26)

## Testa
- Constant folding em expressões simples
- Constant sharing (reutilização de constantes)
- Geração eficiente de código para sequências de atribuições
