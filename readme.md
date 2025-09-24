# 🖥️ Compilador da Linguagem SIMPLE

Este projeto implementa, em **Python 3**, as fases de **análise léxica, sintática e semântica** da linguagem de programação **SIMPLE**.

A linguagem SIMPLE é inspirada nas primeiras versões do BASIC, utilizando instruções simples como `rem`, `input`, `let`, `print`, `goto`, `if/goto` e `end`.

> ⚠️ **Importante:** o compilador **não executa** os programas e **não gera código**.
> Sua função é apenas **analisar** o código-fonte e reportar erros **léxicos**, **sintáticos** e **semânticos**.

---

## 📂 Estrutura do Projeto

```
.
├── simple_compiler.py   # Código do analisador
├── simple.txt           # Programa SIMPLE a ser analisado
└── README.md            # Este arquivo
```

---

## 🚀 Como usar

1. **Crie/edite** o arquivo `simple.txt` na raiz do projeto e escreva o código SIMPLE que deseja analisar.

   Exemplo de programa válido:

   ```basic
   10 input n
   20 let y = 0
   30 if n <= 0 goto 60
   40 let y = n * 2
   50 print y
   60 end
   ```

2. **Execute** o compilador:

   ```bash
   python3 simple_compiler.py
   ```

3. **Saída esperada**:

   * ✅ **Sem erros**:

     ```
     Nenhum erro encontrado. Análise léxica, sintática e semântica: OK.
     ```

   * ❌ **Com erros**:
     Lista cada erro com:

     * Tipo (`LEX`, `SYNTAX`, `SEMANTIC`)
     * Linha no arquivo e rótulo (label)
     * Coluna exata
     * Mensagem explicativa
       *(com uma seta `^` indicando onde o problema ocorreu)*

---

## 📚 Instruções da Linguagem SIMPLE

| Instrução                | Sintaxe                                 | Exemplo Válido                        | Exemplo Inválido                                                 |
| ------------------------ | --------------------------------------- | ------------------------------------- | ---------------------------------------------------------------- |
| **Comentário**           | `rem ...`                               | `10 rem este é um comentário`         | `10 REM maiúsculas não são permitidas`                           |
| **Entrada**              | `input <var>`                           | `10 input x`                          | `10 input 123`                                                   |
| **Saída**                | `print <var>`                           | `20 print x`                          | `20 print x + 1`                                                 |
| **Atribuição**           | `let <var> = <expr>`                    | `30 let x = y + 1`<br>`40 let x = -y` | `30 let x = y + z * 2` ❌ (mais de uma operação)                  |
| **Desvio incondicional** | `goto <linha>`                          | `50 goto 30`                          | `50 goto x`                                                      |
| **Desvio condicional**   | `if <expr> <relop> <expr> goto <linha>` | `60 if x >= 10 goto 100`              | `60 if x + y > z * 2 goto 100` ❌ (mais de uma operação por lado) |
| **Fim do programa**      | `end`                                   | `99 end`                              | `99 end 123`                                                     |

> **Expressões (`<expr>`):**
>
> * Só podem conter **um operando** ou **uma única operação binária**.
> * Exemplos válidos: `x`, `10`, `-x`, `x + 1`, `a * b`
> * Exemplos inválidos: `x + y * z`, `(x + y)` (parênteses não são suportados)

---

## 🔎 Regras de Semântica

* Os **rótulos (labels)** devem ser **únicos** e **estritamente crescentes**.
* `goto` e `if ... goto` só podem apontar para **rótulos existentes**.
* Deve haver **no máximo um `end`**, que deve ser a **última linha executável**.

---

## 🧪 Exemplo de Erro Sintático

Entrada (`simple.txt`):

```basic
10 let y = y + k * 1
20 end
```

Saída:

```
Erros detectados:

-  [SYNTAX] linha 1 rótulo=10 coluna 15: apenas uma operação é permitida por expressão; encontrado '*'
  10 let y = y + k * 1
                ^
Total de erros: 1
```

---

## 👨‍🎓 Autor

**Victor Laurentino do Nascimento**
- 2312130047

---

## 📌 Próximos Passos

* [ ] Implementar **interpretador** para executar os programas SIMPLE.
* [ ] Adicionar suporte a **geração de código intermediário**.
* [ ] Criar **testes automatizados** (unittest/pytest) para facilitar manutenção.

