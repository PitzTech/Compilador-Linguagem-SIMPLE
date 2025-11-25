# 🚀 Quick Start - Compilador SIMPLE → SML

## Uso Básico

### 1. Compilar o Exemplo Padrão
```bash
python3 compilador.py
```
Compila `simple.txt` e gera `binary.txt`

### 2. Compilar Outro Arquivo
```bash
python3 compilador.py testes/test01_soma_simples.txt
```

### 3. Ver Código SML Gerado
```bash
cat binary.txt
```

---

## 📝 Criar Seu Próprio Programa

Crie um arquivo `meu_programa.txt`:

```simple
10 rem meu primeiro programa
20 input x
30 let y = x * 2
40 print y
50 end
```

Compile:
```bash
python3 compilador.py meu_programa.txt
```

---

## ✅ Executar Todos os Testes

```bash
./test_suite.sh
```

---

## 📖 Exemplos Prontos

### Soma de Dois Números
```bash
python3 compilador.py testes/test01_soma_simples.txt
```

### Programa com Loop
```bash
python3 compilador.py testes/test02_media.txt
```

### Todas as Operações
```bash
python3 compilador.py testes/test03_operacoes.txt
```

---

## ❌ Testar Detecção de Erros

```bash
python3 compilador.py testes/error01_maiusculas.txt
python3 compilador.py testes/error02_multiplas_ops.txt
```

---

## 📊 Saída do Compilador

O compilador mostra:
- ✅ Fase 1: Análise (léxica, sintática, semântica)
- ✅ Fase 2: Geração de código SML
- ✅ Estatísticas (variáveis, temporários, constantes)
- ✅ Código SML gerado com comentários
- ✅ Taxa de uso de memória

E salva o código em **`binary.txt`**

---

## 🔧 Arquivo de Saída

O arquivo `binary.txt` contém código SML puro:
```
+1007
+1008
+2007
+3008
+2109
+1109
+4300
+0000
+0000
+0000
```

Este código pode ser executado em um simulador Simpletron.

---

## 📚 Documentação Completa

- **README.md** - Documentação detalhada
- **TESTING.md** - Relatório de testes
- **SML.md** - Especificação do Simpletron Machine Language

---

**Pronto para usar! 🎉**
