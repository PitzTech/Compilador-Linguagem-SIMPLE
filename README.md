# 🖥️ Compilador da Linguagem SIMPLE para SML

[![Python 3](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Compilador completo** que traduz programas escritos na linguagem **SIMPLE** para **Simpletron Machine Language (SML)**, uma linguagem de máquina para o Simpletron (máquina virtual educacional com acumulador e 100 palavras de memória).

## 📋 Autor

**Victor Laurentino do Nascimento** - RA: 2312130047

---

## 🎯 Características

✨ **Análise Completa**
- ✅ Análise Léxica: Tokenização com detecção precisa de erros
- ✅ Análise Sintática: Validação de gramática SIMPLE
- ✅ Análise Semântica: Verificação de labels, gotos e end

🚀 **Otimizações Agressivas**
- ✅ Constant Folding: Avalia expressões constantes em tempo de compilação
- ✅ Reutilização de Temporários: Minimiza uso de memória
- ✅ Eliminação de Código Morto: Remove instruções desnecessárias
- ✅ **Prevenção de Memory Overflow**: Limita uso a 100 palavras

💾 **Geração de Código SML**
- ✅ Código otimizado para Simpletron
- ✅ Alocação inteligente de variáveis e constantes
- ✅ Saída formatada em `binary.txt`

---

## 📂 Estrutura do Projeto

```
.
├── compilador.py              # Compilador principal (análise + síntese)
├── compilador_analise.py      # Analisador léxico/sintático/semântico (legado)
├── compilador_sintese.py      # Gerador de código (legado)
├── compilador_completo.py     # Versão integrada (legado)
├── simple.txt                 # Arquivo de entrada padrão
├── binary.txt                 # Arquivo de saída SML gerado
├── SML.md                     # Documentação do Simpletron Machine Language
├── README.md                  # Este arquivo
└── testes/                    # Suite de testes
    ├── test01_soma_simples.txt
    ├── test02_media.txt
    ├── test03_operacoes.txt
    ├── test04_comparacoes.txt
    ├── test05_negativo.txt
    ├── error01_maiusculas.txt
    ├── error02_multiplas_ops.txt
    ├── error03_label_duplicado.txt
    ├── error04_goto_invalido.txt
    └── error05_end_nao_final.txt
```

---

## 🚀 Como Usar

### 1. **Compilar um Programa SIMPLE**

```bash
python3 compilador.py simple.txt
```

### 2. **Compilar Outro Arquivo**

```bash
python3 compilador.py testes/test01_soma_simples.txt
```

### 3. **Saída**

O código SML será gerado em **`binary.txt`** no formato:

```
+1008
+2008
+3009
+2109
+4300
+0000
+0000
```

---

## 📖 Linguagem SIMPLE

### Comandos Disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| **rem** | Comentário (ignorado) | `10 rem isto é comentário` |
| **input** | Lê inteiro do teclado | `20 input x` |
| **print** | Imprime variável | `30 print x` |
| **let** | Atribuição com expressão | `40 let y = x + 5` |
| **goto** | Desvio incondicional | `50 goto 20` |
| **if/goto** | Desvio condicional | `60 if x > 0 goto 80` |
| **end** | Termina programa | `99 end` |

### Operadores

**Aritméticos:** `+`, `-`, `*`, `/`, `%`
**Relacionais:** `==`, `!=`, `<`, `<=`, `>`, `>=`

### Regras Importantes

⚠️ **Restrições:**
- ✅ Apenas **letras minúsculas** (maiúsculas causam erro léxico)
- ✅ Variáveis são **uma única letra** (a-z)
- ✅ Expressões permitem **no máximo 1 operação** binária
- ✅ Labels devem ser **únicos e crescentes**
- ✅ **`end` deve ser a última** instrução
- ✅ Máximo de **100 palavras** de memória

---

## 📝 Exemplos

### Exemplo 1: Soma Simples

**Arquivo:** `simple.txt`

```simple
10 rem programa de soma
20 input a
30 input b
40 let c = a + b
50 print c
60 end
```

**Execução:**

```bash
$ python3 compilador.py
╔══════════════════════════════════════════════════════════════════════════════╗
║                      COMPILADOR SIMPLE → SML                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Arquivo fonte: simple.txt

→ FASE 1: Análise (Léxica, Sintática, Semântica)
  ✓ 5 statements analisados
  ✓ 5 labels válidos

→ FASE 2: Geração de Código SML Otimizado
  ✓ 8 instruções geradas
  ✓ 3 variáveis alocadas
  ✓ 0 temporários alocados
  ✓ 0 constantes alocadas
  ✓ 11/100 palavras usadas (11%)

→ OTIMIZAÇÕES APLICADAS:
  ✓ Constant folding em expressões
  ✓ Reutilização de registradores temporários
  ✓ Eliminação de instruções redundantes
  ✓ Taxa de uso de memória: 11%

╔════╦══════════╦════════════════════════════════════════════════════╗
║ ## ║  CÓDIGO  ║ COMENTÁRIO                                         ║
╠════╬══════════╬════════════════════════════════════════════════════╣
║  0 ║ +1008 ║ read a                                             ║
║  1 ║ +1009 ║ read b                                             ║
║  2 ║ +2008 ║ load a                                             ║
║  3 ║ +3009 ║ add b                                              ║
║  4 ║ +2110 ║ store c                                            ║
║  5 ║ +1110 ║ write c                                            ║
║  6 ║ +4300 ║ halt                                               ║
║  7 ║ +0000 ║ var a                                              ║
║  8 ║ +0000 ║ var b                                              ║
║  9 ║ +0000 ║ var c                                              ║
╚════╩══════════╩════════════════════════════════════════════════════╝

✓ Código SML salvo em: binary.txt
✓ Compilação concluída com sucesso!
```

### Exemplo 2: Programa com Loop

**Arquivo:** `test02_media.txt`

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

Este programa calcula a soma dos primeiros N números pares dividido por N.

---

## 🧪 Testes

### Suite de Testes Válidos

| Teste | Descrição | Arquivo |
|-------|-----------|---------|
| 01 | Soma simples | `test01_soma_simples.txt` |
| 02 | Média com loop | `test02_media.txt` |
| 03 | Todas operações aritméticas | `test03_operacoes.txt` |
| 04 | Todos operadores relacionais | `test04_comparacoes.txt` |
| 05 | Números negativos | `test05_negativo.txt` |

### Suite de Testes de Erro

| Teste | Erro Esperado | Arquivo |
|-------|---------------|---------|
| 01 | Letras maiúsculas | `error01_maiusculas.txt` |
| 02 | Múltiplas operações | `error02_multiplas_ops.txt` |
| 03 | Label duplicado | `error03_label_duplicado.txt` |
| 04 | Goto inválido | `error04_goto_invalido.txt` |
| 05 | End não final | `error05_end_nao_final.txt` |

### Executar Testes

```bash
# Teste válido
python3 compilador.py testes/test01_soma_simples.txt

# Teste de erro
python3 compilador.py testes/error01_maiusculas.txt
```

---

## 🔧 Simpletron Machine Language (SML)

### Formato

- Palavras de **4 dígitos** com sinal: `+XXYY` ou `-XXYY`
- **XX** = Código de operação (10-43)
- **YY** = Endereço de memória (00-99)

### Códigos de Operação

| Código | Nome | Descrição |
|--------|------|-----------|
| **10** | READ | Lê do teclado para memória |
| **11** | WRITE | Escreve de memória para tela |
| **20** | LOAD | Carrega memória → acumulador |
| **21** | STORE | Armazena acumulador → memória |
| **30** | ADD | Acumulador += memória |
| **31** | SUBTRACT | Acumulador -= memória |
| **32** | DIVIDE | Acumulador /= memória |
| **33** | MULTIPLY | Acumulador *= memória |
| **34** | MODULE | Acumulador %= memória |
| **40** | BRANCH | Desvio incondicional |
| **41** | BRANCHNEG | Desvio se acumulador < 0 |
| **42** | BRANCHZERO | Desvio se acumulador == 0 |
| **43** | HALT | Termina programa |

---

## ⚡ Otimizações Implementadas

### 1. **Constant Folding**
Expressões constantes são avaliadas em tempo de compilação:

```simple
10 let x = 2 + 3  # Compilado como: load 5
```

### 2. **Reutilização de Temporários**
Variáveis temporárias são reutilizadas para economizar memória:

```simple
10 let a = x + y
20 let b = z + w  # Reutiliza mesmo temporário
```

### 3. **Eliminação de Código Morto**
Instruções inalcançáveis são removidas automaticamente.

### 4. **Prevenção de Memory Overflow**
O compilador **garante** que o código gerado use no máximo 100 palavras, gerando erro caso exceda.

---

## ❌ Detecção de Erros

### Erros Léxicos
```
[LEX] Linha 2, col 3: maiúscula não permitida: 'I'
  20 INPUT x
     ^
```

### Erros Sintáticos
```
[SYNTAX] Linha 2, col 10: apenas 1 operação permitida, encontrado: '*'
  20 let y = x + 2 * 3
              ^
```

### Erros Semânticos
```
[SEMANTIC] Linha 3, col 5: goto para label inexistente: 99
  30 if x > 0 goto 99
      ^
```

---

## 📜 Licença

Este projeto foi desenvolvido para fins educacionais como parte do curso de Compiladores.

**Instituto de Educação Superior de Brasília (IESB)**

---

## 🤝 Contribuições

Este é um projeto acadêmico. Para dúvidas ou sugestões, entre em contato com o autor.

---

## 📌 Notas Importantes

⚠️ **O compilador NÃO executa os programas**. Ele apenas:
1. ✅ Analisa o código SIMPLE
2. ✅ Detecta erros
3. ✅ Gera código SML otimizado em `binary.txt`

Para **executar** o código SML, você precisa de um simulador Simpletron.

---

**Compilado com ❤️ por Victor Laurentino**
