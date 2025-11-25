# Teste 09: Constant Sharing (Compartilhamento de Constantes)

**Descrição:** Teste para verificar se constantes repetidas são compartilhadas.

**Resultado Esperado:** Constantes duplicadas devem compartilhar o mesmo endereço de memória.

```simple
05 rem teste de constant folding
10 let a = 5
15 let b = 10
20 let c = 3
25 let d = 5     # mesmo valor que 'a'
30 let e = 10    # mesmo valor que 'b'
35 let f = 3     # mesmo valor que 'c'
40 rem constantes devem ser compartilhadas
45 print a
50 print b
55 print c
60 print d
65 print e
70 print f
75 end
```

**Comportamento Observado:**
- ✅ **6 variáveis alocadas** (a, b, c, d, e, f)
- ✅ **Apenas 3 constantes alocadas** (5, 10, 3)
- ✅ **28/100 palavras** usadas

**Otimização Comprovada:**

| Valor | Ocorrências | Endereços Alocados | Economia |
|-------|-------------|---------------------|----------|
| 5 | 2x (a, d) | 1 endereço | -1 palavra |
| 10 | 2x (b, e) | 1 endereço | -1 palavra |
| 3 | 2x (c, f) | 1 endereço | -1 palavra |

**Total Economizado:** 3 palavras de memória

**Sem Otimização:** 31 palavras (28 + 3)
**Com Otimização:** 28 palavras

**Taxa de Redução:** ~10%

**Conclusão:** ✅ **Constant sharing funcionando perfeitamente!**

O compilador identifica constantes duplicadas e reutiliza o mesmo endereço de memória, economizando espaço e prevenindo memory overflow.
