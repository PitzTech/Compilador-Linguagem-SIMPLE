# 🧪 Relatório de Testes - Compilador SIMPLE → SML

## ✅ Resultados

**100% dos testes passaram com sucesso!**

- ✅ **5 testes válidos** - Compilação bem-sucedida
- ✅ **5 testes de erro** - Erros detectados corretamente
- ✅ **Total: 10/10 testes passando**

---

## 📊 Testes Válidos

### Test 01: Soma Simples
- **Arquivo:** `testes/test01_soma_simples.txt`
- **Descrição:** Lê dois números e imprime sua soma
- **Resultado:** ✅ **10/100 palavras (10%)**
- **Otimizações:** 0 temporários, 0 constantes

### Test 02: Média com Loop
- **Arquivo:** `testes/test02_media.txt`
- **Descrição:** Calcula média dos N primeiros números com loop
- **Resultado:** ✅ **58/100 palavras (58%)**
- **Otimizações:** 3 temporários reutilizados, 2 constantes

### Test 03: Operações Aritméticas
- **Arquivo:** `testes/test03_operacoes.txt`
- **Descrição:** Testa todas operações: +, -, *, /, %
- **Resultado:** ✅ **34/100 palavras (34%)**
- **Otimizações:** 0 temporários, 3 constantes

### Test 04: Comparações
- **Arquivo:** `testes/test04_comparacoes.txt`
- **Descrição:** Testa todos operadores relacionais
- **Resultado:** ✅ **85/100 palavras (85%)**
- **Otimizações:** 3 temporários reutilizados

### Test 05: Números Negativos
- **Arquivo:** `testes/test05_negativo.txt`
- **Descrição:** Operações com números negativos
- **Resultado:** ✅ **20/100 palavras (20%)**
- **Otimizações:** 0 temporários, 2 constantes

---

## ❌ Testes de Erro

### Error 01: Letras Maiúsculas
- **Arquivo:** `testes/error01_maiusculas.txt`
- **Erro Esperado:** Erro léxico - maiúsculas não permitidas
- **Resultado:** ✅ **13 erros detectados corretamente**

### Error 02: Múltiplas Operações
- **Arquivo:** `testes/error02_multiplas_ops.txt`
- **Erro Esperado:** Erro sintático - mais de uma operação
- **Resultado:** ✅ **1 erro detectado corretamente**

### Error 03: Label Duplicado
- **Arquivo:** `testes/error03_label_duplicado.txt`
- **Erro Esperado:** Erro semântico - label repetido
- **Resultado:** ✅ **2 erros detectados corretamente**

### Error 04: Goto Inválido
- **Arquivo:** `testes/error04_goto_invalido.txt`
- **Erro Esperado:** Erro semântico - goto para label inexistente
- **Resultado:** ✅ **1 erro detectado corretamente**

### Error 05: End Não Final
- **Arquivo:** `testes/error05_end_nao_final.txt`
- **Erro Esperado:** Erro semântico - end não é última instrução
- **Resultado:** ✅ **1 erro detectado corretamente**

---

## 🚀 Otimizações Verificadas

### ✅ Constant Folding
Expressões constantes avaliadas em tempo de compilação

### ✅ Reutilização de Temporários
Máximo de 3 temporários mesmo em programas complexos

### ✅ Alocação Inteligente
Uso eficiente de memória (10% a 85% em diferentes testes)

### ✅ Prevenção de Overflow
Todos os testes usam < 100 palavras

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| Testes Totais | 10 |
| Taxa de Sucesso | 100% |
| Uso Médio de Memória | ~40% |
| Uso Máximo de Memória | 85% |
| Temporários Máximos | 3 |

---

## 🔧 Como Executar os Testes

### Teste Individual
```bash
python3 compilador.py testes/test01_soma_simples.txt
```

### Suite Completa
```bash
./test_suite.sh
```

---

**Todos os testes validados em:** 2025-11-25  
**Compilador:** SIMPLE → SML v1.0  
**Autor:** Victor Laurentino do Nascimento
