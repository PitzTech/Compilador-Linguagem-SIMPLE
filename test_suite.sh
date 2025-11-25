#!/bin/bash
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         SUITE DE TESTES - COMPILADOR SIMPLE → SML             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

# Testes válidos
echo "→ TESTES VÁLIDOS:"
for test in testes/test*.txt; do
    echo -n "  Testing $(basename $test)... "
    if python3 compilador.py "$test" > /dev/null 2>&1; then
        echo "✓ PASS"
        ((PASS++))
    else
        echo "✗ FAIL"
        ((FAIL++))
    fi
done

echo ""
echo "→ TESTES DE ERRO (devem falhar):"
for test in testes/error*.txt; do
    echo -n "  Testing $(basename $test)... "
    if python3 compilador.py "$test" > /dev/null 2>&1; then
        echo "✗ FAIL (não detectou erro)"
        ((FAIL++))
    else
        echo "✓ PASS (erro detectado corretamente)"
        ((PASS++))
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ RESULTADO: $PASS testes passaram, $FAIL falharam               "
echo "╚════════════════════════════════════════════════════════════════╝"
