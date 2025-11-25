# Erro 02: Múltiplas Operações

**Descrição:** Usa mais de uma operação por expressão (não permitido).

**Resultado Esperado:** Erro sintático detectado.

```simple
10 input x
20 let y = x + 2 * 3
30 print y
40 end
```

**Erro Esperado:** Apenas uma operação por expressão permitida
