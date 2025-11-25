# Erro 04: Goto para Label Inexistente

**Descrição:** Usa goto para label que não existe.

**Resultado Esperado:** Erro semântico detectado.

```simple
10 input x
20 if x > 0 goto 99
30 print x
40 end
```

**Erro Esperado:** goto para label inexistente: 99
