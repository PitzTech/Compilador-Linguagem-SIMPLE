# Teste 02: Média de N Números (exemplo do simple.txt)

**Descrição:** Calcula a média dos n primeiros números positivos.

**Resultado Esperado:** Compilação bem-sucedida.

```simple
05 rem programa de media
10 input n
15 if n > 0 goto 30
20 let m = -1
25 goto 70
30 let s = 0
35 let i = 1
40 if i == n goto 65
45 let a = 2 * i
50 let s = s + a
55 let i = i + 1
60 goto 40
65 let m = s / n
70 print m
75 end
```

**Teste:**
- Entrada: 5
- Saída esperada: cálculo da soma dos 5 primeiros números pares dividido por 5
