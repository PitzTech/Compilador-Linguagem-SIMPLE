# Github
https://github.com/PitzTech/Compilador-Linguagem-SIMPLE

# Aluno
Victor Laurentino do Nascimento - 2312130047

# SIMPLE Compiler (Analisador Léxico, Sintático e Semântico)

Este projeto implementa em **Python 3** as fases de **análise léxica, sintática e semântica** da linguagem de programação **SIMPLE**.

A linguagem SIMPLE é semelhante às primeiras versões do BASIC e utiliza comandos como `rem`, `input`, `let`, `print`, `goto`, `if/goto` e `end`.

O compilador desenvolvido aqui **não gera código** nem executa os programas. Ele é responsável apenas por analisar o código-fonte e identificar **erros de sintaxe** e **erros semânticos**.

---

## Como rodar

```bash
python3 simple_compiler.py
```

Ao executar, o script automaticamente testa alguns exemplos pré-definidos (um programa correto, três com erros sintáticos e um com erro semântico).

---

## Como adicionar seus próprios programas SIMPLE

1. Abra o arquivo **`simple_compiler.py`** no editor de texto de sua preferência.

2. Vá até o dicionário `TEST_SOURCES` (no final do arquivo). Ele possui vários exemplos já prontos, como `ok_program`, `sintatic_1_bad_token`, etc.

3. Adicione uma nova entrada ao dicionário com o nome que preferir e o código-fonte SIMPLE que deseja testar. Exemplo:

```python
TEST_SOURCES = {
    'ok_program': '''10 input a\n20 input b\n30 let c = a + b\n40 print c\n99 end\n''',

    'meu_teste': '''10 input x\n20 let y = x * 2\n30 print y\n99 end\n''',
}
```

> **Atenção:** use `\n` no final de cada linha do código SIMPLE dentro da string.

4. Salve o arquivo.

5. Rode novamente o script:

```bash
python3 simple_compiler.py
```

6. O compilador vai exibir os resultados da análise do seu código.

---

## Estrutura de análise

- **Léxica:** divide o código em tokens (palavras-chave, variáveis, números, operadores, etc.).
- **Sintática:** valida se as instruções seguem a gramática da linguagem SIMPLE.
- **Semântica:** verifica consistência (ordem de linhas, destino de `goto` existente, variáveis válidas, etc.).

---

## Exemplo de saída

Se o código estiver correto:
```
Análise léxica/sintática: OK
Checagem semântica: OK
```

Se houver erro sintático ou semântico, o erro será listado com o número da linha e a causa.

---

## Próximos passos

- Implementar um **interpretador** para executar os programas SIMPLE analisados.
- Adicionar suporte a **geração de código intermediário**.

---
