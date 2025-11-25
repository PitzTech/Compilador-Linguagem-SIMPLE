# Erro 01: Letras Maiúsculas

**Descrição:** Usa letras maiúsculas fora de comentário (não permitido).

**Resultado Esperado:** Erro léxico detectado.

```simple
10 rem comentario OK
20 INPUT x
30 PRINT x
40 END
```

**Erro Esperado:** Letras maiúsculas não permitidas (INPUT, PRINT, END)
