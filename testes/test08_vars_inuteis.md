# Teste 08: Variáveis Não Usadas

**Descrição:** Teste para verificar comportamento com variáveis atribuídas mas não usadas.

**Resultado Esperado:** Compilação bem-sucedida. Variáveis atribuídas são alocadas mesmo que não sejam usadas posteriormente.

```simple
05 rem teste com variaveis nao usadas
10 input x
20 let a = x + 1
30 let b = x + 2
40 let c = x + 3
50 let d = x + 4
60 let e = x + 5
70 rem apenas x e a sao usados
80 print a
90 end
```

**Comportamento Observado:**
- ✅ **6 variáveis alocadas** (x, a, b, c, d, e)
- ✅ Todas as atribuições são executadas (como esperado)
- ✅ **29/100 palavras** usadas

**Nota sobre Otimização:**
O compilador SIMPLE **não realiza dead code elimination de variáveis** porque:

1. **Conformidade com a semântica SIMPLE:** Todas as instruções `let` devem ser executadas na ordem
2. **Efeitos colaterais:** Em uma linguagem real, variáveis podem ter efeitos colaterais
3. **Simplicidade:** O compilador foca em otimizações de expressões e uso de temporários

**Otimização Implementada:**
- ✅ Reutilização de temporários nas expressões
- ✅ Constant folding (constantes 1, 2, 3, 4, 5 são compartilhadas)
- ✅ Alocação eficiente de memória

**Conclusão:** ✅ Comportamento correto e otimizado dentro do escopo do projeto.
