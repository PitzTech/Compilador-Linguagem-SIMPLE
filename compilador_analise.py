"""
Analisador (fase frontal) para a linguagem SIMPLE
- Léxico: tokeniza linhas numeradas, inteiros, variáveis (letra única minúscula), operadores, palavras-chave
- Sintático: verifica a gramática das instruções (rem, input, let, print, goto, if/goto, end)
- Semântico: verifica consistência de linhas (ordem crescente), alvo de goto/if existe, nomes válidos (letras minúsculas), tokens válidos

Inclui um pequeno conjunto de testes embutidos: 3 fontes com erros sintáticos e 1 com erro semântico (goto para linha inexistente).

Como usar:
$ python3 simple_compiler.py

Saída: para cada fonte de teste, mostra fases (lex, parse, semântica) e erros detectados.

Observações: implementado de forma didática — não é um compilador completo, mas cobre os requisitos pedidos.
"""

import re
from typing import List, Tuple, Optional, Dict

# --------------------- Lexer ---------------------
TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('NAME',     r'[a-z]'),           # variável: uma letra minúscula
    ('KEYWORD',  r'rem|input|let|print|goto|if|end'),
    ('EQ',       r'=='),
    ('NE',       r'!='),
    ('GE',       r'>='),
    ('LE',       r'<='),
    ('GT',       r'>'),
    ('LT',       r'<'),
    ('ASSIGN',   r'='),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('MUL',      r'\*'),
    ('DIV',      r'/'),
    ('MOD',      r'%'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('COMMA',    r','),
    ('WS',       r'[ \t]+'),
    ('UNKNOWN',  r'.'),
]

MASTER_RE = re.compile('|'.join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

class Token:
    def __init__(self, typ, val, col):
        self.type = typ
        self.value = val
        self.col = col
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, col={self.col})"


def lex_line(line_text: str) -> Tuple[Optional[int], List[Token], Optional[str]]:
    """
    Tokeniza uma linha do arquivo SIMPLE. Retorna (line_number, tokens, error_message).
    Se a linha começar com número de linha válido, parseia-o.
    Comentários rem: o resto da linha é tratado como REM e ignorado (mas aceito).
    """
    line_text = line_text.rstrip('\n')
    if not line_text.strip():
        return None, [], None
    # extrai número de linha no começo
    m = re.match(r'\s*(\d+)\s+(.*)', line_text)
    if not m:
        return None, [], f"linha não começa com número de linha seguido por espaço: {line_text!r}"
    lineno = int(m.group(1))
    rest = m.group(2)

    tokens: List[Token] = []
    pos = 0
    # quick check: if starts with rem, rest is comment
    if rest.startswith('rem'):
        tokens.append(Token('KEYWORD', 'rem', 0))
        tokens.append(Token('REM_TEXT', rest[3:].lstrip(), 3))
        return lineno, tokens, None

    for mo in MASTER_RE.finditer(rest):
        kind = mo.lastgroup
        val = mo.group()
        col = mo.start()
        if kind == 'WS':
            continue
        if kind == 'UNKNOWN':
            return lineno, tokens, f"token desconhecido {val!r} na coluna {col}"
        # KEYWORD must be full word -- regex already enforces lowercase
        tokens.append(Token(kind, val, col))
    return lineno, tokens, None

# --------------------- Parser ---------------------

class ASTNode:
    pass

class Program:
    def __init__(self):
        self.lines: List[Tuple[int, 'Stmt']] = []  # (lineno, stmt)

class Stmt(ASTNode):
    pass

class Rem(Stmt):
    def __init__(self, text: str):
        self.text = text

class Input(Stmt):
    def __init__(self, var: str):
        self.var = var

class Let(Stmt):
    def __init__(self, var: str, expr: 'Expr'):
        self.var = var
        self.expr = expr

class Print(Stmt):
    def __init__(self, var: str):
        self.var = var

class Goto(Stmt):
    def __init__(self, target: int):
        self.target = target

class IfGoto(Stmt):
    def __init__(self, left: 'Expr', op: str, right: 'Expr', target: int):
        self.left = left
        self.op = op
        self.right = right
        self.target = target

class End(Stmt):
    pass

# Expressions
class Expr(ASTNode):
    pass

class Num(Expr):
    def __init__(self, val: int):
        self.val = val

class Var(Expr):
    def __init__(self, name: str):
        self.name = name

class BinOp(Expr):
    def __init__(self, left: Expr, op: str, right: Expr):
        self.left = left
        self.op = op
        self.right = right

# Parser helpers
class ParserError(Exception):
    pass


def parse_program(lines: List[str]) -> Tuple[Optional[Program], List[str]]:
    program = Program()
    errors: List[str] = []
    prev_lineno = -1
    for idx, text in enumerate(lines):
        lineno, tokens, lex_err = lex_line(text)
        if lex_err:
            errors.append(f"Lex error na linha {idx+1}: {lex_err}")
            continue
        if lineno is None:
            continue
        if lineno <= prev_lineno:
            errors.append(f"Número de linha não está em ordem crescente: {lineno} depois de {prev_lineno}")
            # continue parsing to collect more errors
        prev_lineno = lineno
        try:
            stmt = parse_stmt(tokens)
            program.lines.append((lineno, stmt))
        except ParserError as e:
            errors.append(f"Sintaxe: linha {lineno}: {e}")
    return (program if not errors else program), errors


def expect_token(tokens: List[Token], pos: int, *kinds) -> Tuple[Token, int]:
    if pos >= len(tokens):
        raise ParserError(f"esperava {' ou '.join(kinds)}, encontrou fim da linha")
    tok = tokens[pos]
    if tok.type in kinds or tok.value in kinds:
        return tok, pos+1
    raise ParserError(f"esperava {' ou '.join(kinds)}, encontrou {tok.type}({tok.value}) na coluna {tok.col}")

# Expression parser: recursive descent with precedence

OP_PRECEDENCE = {
    '%': 3, '*': 3, '/': 3,
    '+': 2, '-': 2,
}


def parse_stmt(tokens: List[Token]) -> Stmt:
    if not tokens:
        raise ParserError("linha vazia depois do número")
    # first token should be keyword
    first = tokens[0]
    if first.type != 'KEYWORD':
        raise ParserError(f"esperava uma instrução (rem/input/let/print/goto/if/end), encontrou {first.value}")
    kw = first.value
    if kw == 'rem':
        # rem parsing: second token is REM_TEXT
        if len(tokens) >= 2 and tokens[1].type == 'REM_TEXT':
            return Rem(tokens[1].value)
        else:
            return Rem('')
    if kw == 'input':
        # input x
        if len(tokens) != 2 or tokens[1].type != 'NAME':
            raise ParserError("uso: input <var> (var é uma letra minúscula)")
        return Input(tokens[1].value)
    if kw == 'print':
        if len(tokens) != 2 or tokens[1].type != 'NAME':
            raise ParserError("uso: print <var> (var é uma letra minúscula)")
        return Print(tokens[1].value)
    if kw == 'goto':
        # goto <number>
        if len(tokens) != 2 or tokens[1].type != 'NUMBER':
            raise ParserError("uso: goto <número de linha>")
        return Goto(int(tokens[1].value))
    if kw == 'end':
        if len(tokens) != 1:
            raise ParserError("end não recebe argumentos")
        return End()
    if kw == 'let':
        # let x = expr
        # tokens: KEYWORD NAME ASSIGN ...
        if len(tokens) < 4:
            raise ParserError("uso: let <var> = <expressão>")
        if tokens[1].type != 'NAME' or tokens[2].type != 'ASSIGN':
            raise ParserError("uso: let <var> = <expressão> (nome de variável e '=')")
        var = tokens[1].value
        expr_tokens = tokens[3:]
        expr, rem = parse_expr(expr_tokens, 0)
        if rem != len(expr_tokens):
            extra = expr_tokens[rem]
            raise ParserError(f"token extra após expressão: {extra.value} na coluna {extra.col}")
        return Let(var, expr)
    if kw == 'if':
        # if <expr> <relop> <expr> goto <number>
        # find 'goto' token
        # tokens like: KEYWORD ... maybe 'if' then expression tokens including NAME/NUMBER/BINOPS, then relational op token(s), then expression, then KEYWORD goto, then NUMBER
        # Simpler: parse left expr until relational operator token types (EQ, NE, GT, LT, GE, LE)
        pos = 1
        left_expr, pos = parse_expr(tokens, pos)
        if pos >= len(tokens):
            raise ParserError("instrução if incompleta: esperava operador relacional")
        reltok = tokens[pos]
        if reltok.type not in ('EQ','NE','GT','LT','GE','LE'):
            raise ParserError(f"operador relacional esperado, encontrado {reltok.value}")
        op = reltok.value
        pos += 1
        right_expr, pos = parse_expr(tokens, pos)
        # next should be KEYWORD goto
        if pos >= len(tokens) or not (tokens[pos].type == 'KEYWORD' and tokens[pos].value == 'goto'):
            raise ParserError("instrução if deve terminar com 'goto <linha>'")
        pos += 1
        if pos >= len(tokens) or tokens[pos].type != 'NUMBER':
            raise ParserError("instrução if: esperava número de linha após goto")
        target = int(tokens[pos].value)
        pos += 1
        if pos != len(tokens):
            extra = tokens[pos]
            raise ParserError(f"texto extra após if: {extra.value} na coluna {extra.col}")
        return IfGoto(left_expr, op, right_expr, target)
    raise ParserError(f"instrução desconhecida: {kw}")

# parse_expr: supports numbers, names, parentheses, binary ops with precedence

def parse_expr(tokens: List[Token], pos: int) -> Tuple[Expr, int]:
    # implement Pratt parser / precedence climbing
    def parse_primary(pos):
        if pos >= len(tokens):
            raise ParserError("expressão incompleta")
        t = tokens[pos]
        if t.type == 'NUMBER':
            return Num(int(t.value)), pos+1
        if t.type == 'NAME':
            return Var(t.value), pos+1
        if t.type == 'LPAREN':
            expr, npos = parse_expr(tokens, pos+1)
            if npos >= len(tokens) or tokens[npos].type != 'RPAREN':
                raise ParserError("parêntese direito esperado")
            return expr, npos+1
        raise ParserError(f"primária inválida: {t.value} na coluna {t.col}")

    def get_precedence(tok: Token) -> int:
        if tok.type in ('PLUS','MINUS'):
            return OP_PRECEDENCE['+']
        if tok.type in ('MUL','DIV','MOD'):
            return OP_PRECEDENCE['*']
        # unknown operator
        return -1

    left, pos = parse_primary(pos)
    while pos < len(tokens):
        t = tokens[pos]
        if t.type in ('PLUS','MINUS','MUL','DIV','MOD'):
            op = t.value
            prec = get_precedence(t)
            pos += 1
            right, pos = parse_expr_rhs(right_left=left, min_prec=prec, tokens=tokens, pos=pos)
            left = right
        else:
            break
    return left, pos


def parse_expr_rhs(right_left: Expr, min_prec: int, tokens: List[Token], pos: int) -> Tuple[Expr, int]:
    # right_left is left-hand expression; pos is at start of right primary
    # parse primary on right
    def parse_primary_at(pos):
        if pos >= len(tokens):
            raise ParserError("expressão incompleta (rhs)")
        t = tokens[pos]
        if t.type == 'NUMBER':
            return Num(int(t.value)), pos+1
        if t.type == 'NAME':
            return Var(t.value), pos+1
        if t.type == 'LPAREN':
            expr, npos = parse_expr(tokens, pos+1)
            if npos >= len(tokens) or tokens[npos].type != 'RPAREN':
                raise ParserError("parêntese direito esperado (rhs)")
            return expr, npos+1
        raise ParserError(f"primária inválida (rhs): {t.value} na coluna {t.col}")

    left = right_left
    # we already consumed operator before calling this; parse the right primary
    right, pos = parse_primary_at(pos)
    node = BinOp(left, tokens[pos-1].value if pos-1 < len(tokens) else '?', right)

    # now check for further operators with higher precedence
    while pos < len(tokens):
        t = tokens[pos]
        if t.type not in ('PLUS','MINUS','MUL','DIV','MOD'):
            break
        prec = OP_PRECEDENCE.get(t.value, -1)
        if prec > min_prec:
            # consume op
            op = t.value
            pos += 1
            rhs, pos = parse_expr_rhs(node, prec, tokens, pos)
            node = rhs
        else:
            break
    return node, pos

# --------------------- Semantic Analyzer ---------------------

class SemanticError(Exception):
    pass


def semantic_check(program: Program) -> List[str]:
    errors: List[str] = []
    # check that line numbers are strictly increasing and unique
    linenos = [ln for ln, _ in program.lines]
    if len(linenos) != len(set(linenos)):
        errors.append("números de linha duplicados detectados")
    if any(earlier >= later for earlier, later in zip(linenos, linenos[1:])):
        errors.append("números de linha não estão estritamente crescentes")

    # collect targets from gotos and ensure they exist
    labels = set(linenos)
    for ln, stmt in program.lines:
        if isinstance(stmt, Goto):
            if stmt.target not in labels:
                errors.append(f"linha {ln}: goto para linha inexistente {stmt.target}")
        if isinstance(stmt, IfGoto):
            if stmt.target not in labels:
                errors.append(f"linha {ln}: if/goto para linha inexistente {stmt.target}")
    # check variable names are single lowercase letter and keywords are correct -- lexer already enforces most
    # check print/input/let variable names length
    for ln, stmt in program.lines:
        if isinstance(stmt, Input) or isinstance(stmt, Print):
            if not re.fullmatch(r'[a-z]', stmt.var):
                errors.append(f"linha {ln}: nome de variável inválido: {stmt.var}")
        if isinstance(stmt, Let):
            if not re.fullmatch(r'[a-z]', stmt.var):
                errors.append(f"linha {ln}: nome de variável inválido na atribuição: {stmt.var}")
            # further semantic checks on expression variables
            check_expr_vars(stmt.expr, ln, errors)
        if isinstance(stmt, IfGoto):
            check_expr_vars(stmt.left, ln, errors)
            check_expr_vars(stmt.right, ln, errors)
    return errors


def check_expr_vars(expr: Expr, ln: int, errors: List[str]):
    if isinstance(expr, Var):
        if not re.fullmatch(r'[a-z]', expr.name):
            errors.append(f"linha {ln}: variável inválida na expressão: {expr.name}")
    elif isinstance(expr, Num):
        pass
    elif isinstance(expr, BinOp):
        check_expr_vars(expr.left, ln, errors)
        check_expr_vars(expr.right, ln, errors)
    else:
        errors.append(f"linha {ln}: expressão desconhecida")

# --------------------- Test sources ---------------------

TEST_SOURCES = {
    'ok_program': '''10 rem determina e imprime a soma de dois inteiros
15 rem
20 rem
30 input a
40 input b
45 rem
50 rem
60 let c = a + b
65 rem
70 rem
80 print c
90 rem
99 end
''',

    # Sintático 1: token inválido (letra maiúscula K) -> lex error
    'sintatic_1_bad_token': '''10 rem teste
20 input A
30 end
''',

    # Sintático 2: malformed if (missing goto)
    'sintatic_2_bad_if': '''10 input a
20 input b
30 if a == b 80
40 print a
99 end
''',

    # Sintático 3: let with bad expression (unexpected token)
    'sintatic_3_bad_let': '''10 let x = 5 + * 3
20 print x
99 end
''',

    # Semântico: goto to non-existent line 999
    'semantico_bad_goto': '''10 input a
20 goto 999
30 print a
99 end
''',
}

# --------------------- Runner / tests ---------------------

def run_on_source(src: str) -> None:
    print('--- Fonte ---')
    print(src)
    lines = src.splitlines()
    program, parse_errors = parse_program(lines)
    if parse_errors:
        print('\nErros na fase léxica/sintática:')
        for e in parse_errors:
            print('  -', e)
    else:
        print('\nAnálise léxica/sintática: OK')
    sem_errors = semantic_check(program)
    if sem_errors:
        print('\nErros semânticos:')
        for e in sem_errors:
            print('  -', e)
    else:
        print('\nChecagem semântica: OK')

if __name__ == '__main__':
    for name, src in TEST_SOURCES.items():
        print('\n========================')
        print('Teste:', name)
        run_on_source(src)

    print('\nConcluído.')
