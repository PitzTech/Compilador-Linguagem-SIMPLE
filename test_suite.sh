#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════
# TEST SUITE COMPLETO - Compilador SIMPLE → SML
# ════════════════════════════════════════════════════════════════════════════

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0;33' # No Color

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Arrays para armazenar resultados
declare -a RESULTS
declare -a MEMORY_USAGE

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUITE - COMPILADOR SIMPLE → SML                    ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# FUNÇÃO: Testar arquivo válido
# ════════════════════════════════════════════════════════════════════════════
test_valid() {
    local file=$1
    local name=$(basename "$file" .txt)

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -ne "Testing ${BLUE}${name}${NC}... "

    # Compila e captura output
    if OUTPUT=$(python3 compilador.py "$file" 2>&1); then
        # Extrai uso de memória
        MEM=$(echo "$OUTPUT" | grep -oP '\d+/100 palavras usadas' | head -1)
        MEM_PCT=$(echo "$MEM" | grep -oP '^\d+')

        # Valida que tem binary.txt
        if [ -f "binary.txt" ]; then
            echo -e "${GREEN}✓ OK${NC} (${MEM})"
            RESULTS+=("${name}: ✓ OK (${MEM})")
            MEMORY_USAGE+=("${name}|${MEM_PCT}")
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}✗ FAIL${NC} (binary.txt não gerado)"
            RESULTS+=("${name}: ✗ FAIL (binary.txt não gerado)")
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (compilação falhou)"
        RESULTS+=("${name}: ✗ FAIL (compilação falhou)")
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# ════════════════════════════════════════════════════════════════════════════
# FUNÇÃO: Testar arquivo de erro
# ════════════════════════════════════════════════════════════════════════════
test_error() {
    local file=$1
    local name=$(basename "$file" .txt)

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -ne "Testing ${YELLOW}${name}${NC}... "

    # Compila e espera erro
    if OUTPUT=$(python3 compilador.py "$file" 2>&1); then
        echo -e "${RED}✗ FAIL${NC} (deveria detectar erro)"
        RESULTS+=("${name}: ✗ FAIL (deveria detectar erro)")
        FAILED_TESTS=$((FAILED_TESTS + 1))
    else
        # Verifica se detectou erro
        if echo "$OUTPUT" | grep -q "erro(s) encontrado(s)"; then
            ERRS=$(echo "$OUTPUT" | grep -oP '\d+ erro\(s\)' | grep -oP '^\d+')
            echo -e "${GREEN}✓ OK${NC} (${ERRS} erro(s) detectado(s))"
            RESULTS+=("${name}: ✓ OK (${ERRS} erro(s) detectado(s))")
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}✗ FAIL${NC} (erro não detectado corretamente)"
            RESULTS+=("${name}: ✗ FAIL (erro não detectado corretamente)")
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
}

# ════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO DOS TESTES
# ════════════════════════════════════════════════════════════════════════════

echo "→ Testes Válidos:"
echo ""

for file in testes/test*.txt; do
    test_valid "$file"
done

echo ""
echo "→ Testes de Erro:"
echo ""

for file in testes/error*.txt; do
    test_error "$file"
done

# ════════════════════════════════════════════════════════════════════════════
# ESTATÍSTICAS
# ════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                               ESTATÍSTICAS                                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Calcula taxa de sucesso
SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")

echo "Total de testes: $TOTAL_TESTS"
echo -e "Testes passando: ${GREEN}$PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "Testes falhando: ${RED}$FAILED_TESTS${NC}"
else
    echo "Testes falhando: 0"
fi
echo "Taxa de sucesso: ${SUCCESS_RATE}%"
echo ""

# Calcula estatísticas de memória
if [ ${#MEMORY_USAGE[@]} -gt 0 ]; then
    echo "→ Uso de Memória:"
    echo ""

    # Encontra min, max e média
    MIN_MEM=100
    MAX_MEM=0
    SUM_MEM=0
    COUNT=0

    for entry in "${MEMORY_USAGE[@]}"; do
        MEM=$(echo "$entry" | cut -d'|' -f2)
        if [ "$MEM" -lt "$MIN_MEM" ]; then
            MIN_MEM=$MEM
        fi
        if [ "$MEM" -gt "$MAX_MEM" ]; then
            MAX_MEM=$MEM
        fi
        SUM_MEM=$((SUM_MEM + MEM))
        COUNT=$((COUNT + 1))
    done

    AVG_MEM=$(awk "BEGIN {printf \"%.1f\", $SUM_MEM/$COUNT}")

    echo "Uso mínimo: ${MIN_MEM}%"
    echo "Uso máximo: ${MAX_MEM}%"
    echo "Uso médio: ${AVG_MEM}%"
    echo "Margem de segurança: $((100 - MAX_MEM))% livre"
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        ✓ TODOS OS TESTES PASSARAM!                           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                        ✗ ALGUNS TESTES FALHARAM                              ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Testes que falharam:"
    for result in "${RESULTS[@]}"; do
        if echo "$result" | grep -q "✗"; then
            echo "  - $result"
        fi
    done
    exit 1
fi
