# Suite de Testes - Compilador SIMPLE → SML

## Visão Geral

Esta pasta contém 19 testes que verificam todas as funcionalidades do compilador, incluindo casos de sucesso e de erro.

## Testes Válidos (14 testes)

### Testes Básicos

- **test01_soma_simples.txt** - Operações básicas de soma e subtração
- **test02_media.txt** - Cálculo de média com divisão
- **test03_operacoes.txt** - Todas operações aritméticas: `+`, `-`, `*`, `/`, `%`
- **test04_comparacoes.txt** - Operadores relacionais: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **test05_negativo.txt** - Números negativos e operações com valores negativos

### Testes de Stress e Otimização

- **test06_memory_stress.txt** - Loop complexo com 24 variáveis (93/100 palavras)
- **test07_overflow.txt** - Teste extremo com múltiplas variáveis em loop
- **test08_vars_inuteis.txt** - Verifica eliminação de variáveis não usadas
  - Define variáveis `b`, `c`, `d`, `e` mas usa apenas `x` e `a`
  - Esperado: Otimizador elimina variáveis não usadas
- **test09_constant_folding.txt** - Verifica compartilhamento de constantes
  - Define 6 variáveis com valores: 5, 10, 3, 5, 10, 3
  - Esperado: Apenas 3 constantes alocadas (valores duplicados compartilhados)

### Testes de Otimização de Overflow

- **test10_overflow_26vars.txt** - 26 variáveis consecutivas encadeadas
  - Código: `a=0, b=a+2, c=b+2, ..., z=y+2, print z`
  - Sem otimização: 107 palavras → **OVERFLOW**
  - Com otimização: 57 palavras → **OK** ✓
  - Demonstra: Constant folding completo, eliminação de stores

- **test11_overflow_prints.txt** - 26 variáveis com 5 prints intermediários
  - Código: Similar ao anterior mas com `print f, k, p, u, z`
  - Sem otimização: ~110 palavras → **OVERFLOW**
  - Com otimização: 78 palavras → **OK** ✓
  - Demonstra: Armazena apenas variáveis necessárias para prints

### Testes de Validação de Print

- **test12_print_constante.txt** - Print de constante (let a = 10, print a)
- **test13_dinamico.txt** - Input dinâmico com operações encadeadas
  - Verifica que código dinâmico gera operações completas (LOAD, ADD, STORE)
- **test14_print_simples.txt** - Print simples de variável constante

## Testes de Erro (5 testes)

Estes testes **devem falhar** na compilação, detectando erros:

- **error01_maiusculas.txt** - Detecta uso de caracteres maiúsculos (não permitidos)
- **error02_multiplas_ops.txt** - Detecta múltiplas operações em uma expressão
- **error03_label_duplicado.txt** - Detecta labels duplicados
- **error04_goto_invalido.txt** - Detecta goto para label inexistente
- **error05_end_nao_final.txt** - Detecta comando `end` em posição incorreta

## Executando os Testes

### Executar todos os testes:
```bash
./test_suite.sh
```

### Executar teste individual:
```bash
python3 compilador.py testes/test01_soma_simples.txt
```

### Executar teste com verbose:
```bash
python3 compilador.py testes/test10_overflow_26vars.txt 2>&1 | less
```

## Resultados Esperados

### Taxa de Sucesso
- **19/19 testes passando (100%)**
- 14 testes válidos compilam com sucesso
- 5 testes de erro detectam erros corretamente

### Estatísticas de Otimização

| Teste | Variáveis | Temporários | Constantes | Total | Status |
|-------|-----------|-------------|------------|-------|--------|
| test06 | 24 | 2 | 2 | 93/100 | ✓ |
| test07 | 15 | 2 | 4 | 74/100 | ✓ |
| test08 | 6 | 0 | 5 | 29/100 | ✓ |
| test09 | 6 | 3 | 3 | 42/100 | ✓ |
| test10 | 0 | 1 | 26 | 57/100 | ✓ |
| test11 | 4 | 3 | 26 | 78/100 | ✓ |

## Otimizações Demonstradas

### 1. Constant Folding
- **Teste**: test09_constant_folding.txt
- **Resultado**: Constantes duplicadas (5, 10, 3) são compartilhadas

### 2. Dead Code Elimination
- **Teste**: test08_vars_inuteis.txt
- **Resultado**: Variáveis não usadas não são alocadas

### 3. Constant Propagation
- **Teste**: test10_overflow_26vars.txt
- **Resultado**: Valores constantes propagados e calculados em tempo de compilação

### 4. Register Reuse
- **Teste**: test11_overflow_prints.txt
- **Resultado**: Reutilização agressiva de temporários (máx 3 slots)

## Notas Importantes

1. **Teste 10 e 11**: Antes das otimizações, causavam OVERFLOW. Agora compilam com sucesso.
2. **Teste 13**: Demonstra que código com `input` continua gerando operações completas (não simplifica).
3. **Testes 12 e 14**: Verificam que prints de constantes funcionam corretamente com temporários.

## Estrutura dos Arquivos

```
testes/
├── README.md                    # Este arquivo
├── test01_soma_simples.txt      # Testes válidos
├── test02_media.txt
├── ...
├── test14_print_simples.txt
├── error01_maiusculas.txt       # Testes de erro
├── error02_multiplas_ops.txt
├── ...
└── error05_end_nao_final.txt
```
