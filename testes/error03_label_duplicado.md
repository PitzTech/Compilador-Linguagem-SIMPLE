# Erro 03: Label Duplicado

**Descrição:** Usa o mesmo label duas vezes (não permitido).

**Resultado Esperado:** Erro semântico detectado.

```simple
10 input x
20 let y = x + 1
20 print y
30 end
```

**Erro Esperado:** Label 20 duplicado
