# Teste 02: Média dos N Primeiros Números Pares

**Descrição:** Calcula a média dos n primeiros números pares (2, 4, 6, 8, ..., 2n).

**Algoritmo:**
1. Lê um número n
2. Se n ≤ 0, retorna -1 (erro)
3. Se n > 0, calcula a soma dos primeiros n números pares
4. Divide a soma por n para obter a média

**Código SIMPLE:**
```simple
05 rem programa de media
10 input n
15 if n > 0 goto 30
20 let m = -1
25 goto 70
30 let s = 0
35 let i = 1
40 let a = 2 * i
45 let s = s + a
50 let i = i + 1
55 if i > n goto 65
60 goto 40
65 let m = s / n
70 print m
75 end
```

**Testes:**

| Entrada | Cálculo | Resultado Esperado |
|---------|---------|-------------------|
| n = 1 | (2) / 1 | m = 2 |
| n = 5 | (2+4+6+8+10) / 5 = 30/5 | m = 6 |
| n = 10 | (2+4+6+8+10+12+14+16+18+20) / 10 = 110/10 | m = 11 |
| n = 0 | erro | m = -1 |
| n = -5 | erro | m = -1 |

**Otimizações Aplicadas:**
- Reutilização de temporários no loop
- Constant sharing (0, 1, 2)
- Memory usage: ~52/100 (52%)

**Notas:**
- Demonstra loop com acumulação
- Teste de condição no início (n > 0)
- Teste de condição no final do loop (i > n)
- Exemplo de programa com complexidade moderada
