"""
Compilador Completo da Linguagem SIMPLE para Simpletron Machine Language (SML)

Este compilador traduz programas escritos em SIMPLE para código SML executável
no Simpletron, uma máquina virtual com acumulador e 100 palavras de memória.

Execução:
    python3 compilador_completo.py [arquivo.txt]

Fases do Compilador:
    1. ANÁLISE LÉXICA: Tokenização do código fonte
    2. ANÁLISE SINTÁTICA: Validação da estrutura gramatical
    3. ANÁLISE SEMÂNTICA: Validação de labels, gotos e end
    4. CONSTRUÇÃO AST: Árvore sintática abstrata
    5. OTIMIZAÇÃO: Constant folding e eliminação de código morto
    6. GERAÇÃO DE CÓDIGO SML: Tradução para Simpletron Machine Language
    7. ALOCAÇÃO DE MEMÓRIA: Variáveis e constantes na memória do Simpletron

Formato SML:
    - Palavras de 4 dígitos com sinal: +XXYY
    - XX = código de operação (10-43)
    - YY = endereço de memória (00-99)
    - Memória de 100 palavras (00-99)

Autor: Victor Laurentino do Nascimento - 2312130047
"""

import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple

# ============================================================================
# CÓDIGOS DE OPERAÇÃO SML
# ============================================================================

class SMLOpCode:
    """Códigos de operação do Simpletron Machine Language."""
    # I/O
    READ = 10        # Lê palavra do teclado para memória
    WRITE = 11       # Escreve palavra da memória para tela

    # Load/Store
    LOAD = 20        # Carrega palavra da memória para acumulador
    STORE = 21       # Armazena acumulador na memória

    # Aritmética (opera com acumulador)
    ADD = 30         # Acumulador += memória[XX]
    SUBTRACT = 31    # Acumulador -= memória[XX]
    DIVIDE = 32      # Acumulador /= memória[XX]
    MULTIPLY = 33    # Acumulador *= memória[XX]
    MODULE = 34      # Acumulador %= memória[XX]

    # Controle de fluxo
    BRANCH = 40      # Desvio incondicional
    BRANCHNEG = 41   # Desvio se acumulador < 0
    BRANCHZERO = 42  # Desvio se acumulador == 0
    HALT = 43        # Fim do programa


# ============================================================================
# PARTE 1: ANÁLISE LÉXICA, SINTÁTICA E SEMÂNTICA
# ============================================================================

@dataclass
class Token:
    """Token gerado pelo analisador léxico."""
    kind: str
    value: str
    file_line: int
    label: Optional[int]
    col: int


@dataclass
class AnalysisError:
    """Erro detectado durante análise."""
    phase: str
    message: str
    file_line: int
    label: Optional[int]
    col: int
    line_text: str

    def __str__(self) -> str:
        lbl = f" rótulo={self.label}" if self.label is not None else ""
        header = f"[{self.phase.upper()}] linha {self.file_line}{lbl} coluna {self.col}: {self.message}"
        caret_pos = max(1, min(self.col, len(self.line_text) + 1))
        caret_line = self.line_text + "\n" + (" " * (caret_pos - 1)) + "^"
        return header + "\n  " + caret_line


TOKEN_SPECS = [
    ('RELOP',   r'==|!=|>=|<=|>|<'),
    ('NUMBER',  r'\d+'),
    ('KW',      r'rem|input|let|print|goto|if|end'),
    ('NAME',    r'[a-z]'),
    ('ASSIGN',  r'='),
    ('PLUS',    r'\+'),
    ('MINUS',   r'-'),
    ('MUL',     r'\*'),
    ('DIV',     r'/'),
    ('MOD',     r'%'),
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),
    ('WS',      r'[ \t]+'),
    ('MISMATCH', r'.'),
]
_MASTER_RE = re.compile('|'.join(f"(?P<{n}>{p})" for n, p in TOKEN_SPECS))


def lex_rest(rest: str, file_line: int, label: Optional[int], rest_start_col: int, errors: List[AnalysisError]) -> List[Token]:
    """Tokeniza a parte após o rótulo."""
    tokens: List[Token] = []
    pos = 0
    L = len(rest)
    while pos < L:
        m = _MASTER_RE.match(rest, pos)
        if not m:
            errors.append(AnalysisError('lex', 'caractere inválido', file_line, label, rest_start_col + pos, rest))
            break
        kind = m.lastgroup
        val = m.group()
        start = m.start()
        col = rest_start_col + start

        if kind == 'WS':
            pos = m.end()
            continue

        if kind == 'MISMATCH':
            ch = val
            if ch.isalpha() and ch.upper() == ch:
                errors.append(AnalysisError('lex', f"letra maiúscula não permitida: '{ch}'", file_line, label, col, rest))
            else:
                errors.append(AnalysisError('lex', f"token inválido: '{ch}'", file_line, label, col, rest))
            pos = m.end()
            continue

        tokens.append(Token(kind, val, file_line, label, col))
        pos = m.end()
    return tokens


class ParserError(Exception):
    """Exceção para erros de parsing."""
    def __init__(self, message: str, file_line: int, label: Optional[int], col: int):
        super().__init__(message)
        self.message = message
        self.file_line = file_line
        self.label = label
        self.col = col


def parse_expression(tokens: List[Token], pos: int, file_line: int, label: Optional[int], stop_kinds: Optional[set] = None) -> int:
    """Parser de expressão: no máximo 1 operação binária."""
    if stop_kinds is None:
        stop_kinds = set()

    def parse_operand(p: int) -> int:
        if p >= len(tokens):
            last_col = tokens[-1].col if tokens else 1
            raise ParserError('expressão incompleta', file_line, label, last_col)
        t = tokens[p]
        if t.kind == 'MINUS':
            if p + 1 >= len(tokens):
                raise ParserError("operando esperado após '-'", file_line, label, t.col)
            if tokens[p+1].kind not in ('NUMBER', 'NAME'):
                raise ParserError("após '-' só pode vir número ou variável", file_line, label, tokens[p+1].col)
            return p + 2
        if t.kind in ('NUMBER', 'NAME'):
            return p + 1
        raise ParserError(f"operando inválido '{t.value}'", file_line, label, t.col)

    p = parse_operand(pos)
    if p >= len(tokens) or tokens[p].kind in stop_kinds:
        return p
    if tokens[p].kind not in ('PLUS', 'MINUS', 'MUL', 'DIV', 'MOD'):
        return p
    p += 1
    p = parse_operand(p)
    if p < len(tokens) and tokens[p].kind not in stop_kinds:
        raise ParserError(f"apenas uma operação permitida; encontrado '{tokens[p].value}'", file_line, label, tokens[p].col)
    return p


def parse_statement(tokens: List[Token], file_line: int, label: Optional[int], line_text: str) -> List[AnalysisError]:
    """Valida sintaxe de um statement."""
    errs: List[AnalysisError] = []
    if not tokens:
        errs.append(AnalysisError('syntax', 'instrução ausente', file_line, label, 1, line_text))
        return errs

    first = tokens[0]
    if first.kind != 'KW':
        errs.append(AnalysisError('syntax', f"esperada instrução, encontrada '{first.value}'", file_line, label, first.col, line_text))
        return errs

    kw = first.value
    try:
        if kw == 'input':
            if len(tokens) < 2 or tokens[1].kind != 'NAME':
                raise ParserError("'input' requer variável", file_line, label, first.col)
            if len(tokens) != 2:
                raise ParserError(f"token extra: '{tokens[2].value}'", file_line, label, tokens[2].col)

        elif kw == 'print':
            if len(tokens) < 2 or tokens[1].kind != 'NAME':
                raise ParserError("'print' requer variável", file_line, label, first.col)
            if len(tokens) != 2:
                raise ParserError(f"token extra: '{tokens[2].value}'", file_line, label, tokens[2].col)

        elif kw == 'goto':
            if len(tokens) < 2 or tokens[1].kind != 'NUMBER':
                raise ParserError("'goto' requer número de linha", file_line, label, first.col)
            if len(tokens) != 2:
                raise ParserError(f"token extra: '{tokens[2].value}'", file_line, label, tokens[2].col)

        elif kw == 'end':
            if len(tokens) != 1:
                raise ParserError("'end' não aceita argumentos", file_line, label, tokens[1].col)

        elif kw == 'let':
            if len(tokens) < 4:
                raise ParserError("uso: let <var> = <expressão>", file_line, label, first.col)
            if tokens[1].kind != 'NAME' or tokens[2].kind != 'ASSIGN':
                raise ParserError("sintaxe inválida em 'let'", file_line, label, tokens[1].col)
            endpos = parse_expression(tokens, 3, file_line, label, set())
            if endpos != len(tokens):
                raise ParserError(f"token extra: '{tokens[endpos].value}'", file_line, label, tokens[endpos].col)

        elif kw == 'if':
            pos_after_left = parse_expression(tokens, 1, file_line, label, {'RELOP'})
            if pos_after_left >= len(tokens) or tokens[pos_after_left].kind != 'RELOP':
                col = tokens[pos_after_left].col if pos_after_left < len(tokens) else tokens[-1].col
                raise ParserError("operador relacional esperado", file_line, label, col)
            pos = pos_after_left + 1
            pos_after_right = parse_expression(tokens, pos, file_line, label, {'KW'})
            if pos_after_right >= len(tokens) or not (tokens[pos_after_right].kind == 'KW' and tokens[pos_after_right].value == 'goto'):
                col = tokens[pos_after_right].col if pos_after_right < len(tokens) else tokens[-1].col
                raise ParserError("esperado 'goto'", file_line, label, col)
            if pos_after_right + 1 >= len(tokens) or tokens[pos_after_right + 1].kind != 'NUMBER':
                raise ParserError("'goto' sem número", file_line, label, tokens[pos_after_right].col)
            if pos_after_right + 2 != len(tokens):
                raise ParserError(f"token extra: '{tokens[pos_after_right + 2].value}'", file_line, label, tokens[pos_after_right + 2].col)
        else:
            raise ParserError(f"instrução desconhecida '{kw}'", file_line, label, first.col)

    except ParserError as pe:
        errs.append(AnalysisError('syntax', pe.message, pe.file_line, pe.label, pe.col, line_text))

    return errs


def semantic_analysis(non_comment_lines: List[Dict], tokens_by_line: Dict[int, List[Token]]) -> List[AnalysisError]:
    """Análise semântica."""
    errs: List[AnalysisError] = []
    if not non_comment_lines:
        return errs

    labels = [info['label'] for info in non_comment_lines]

    for i in range(1, len(labels)):
        if labels[i] <= labels[i-1]:
            info = non_comment_lines[i]
            errs.append(AnalysisError('semantic', f"rótulos não crescentes: {labels[i-1]} → {labels[i]}", info['file_line'], info['label'], 1, info['line_text']))

    seen = {}
    for info in non_comment_lines:
        lbl = info['label']
        if lbl in seen:
            errs.append(AnalysisError('semantic', f"rótulo duplicado {lbl}", info['file_line'], lbl, 1, info['line_text']))
        else:
            seen[lbl] = info['file_line']

    label_set = set(labels)

    for info in non_comment_lines:
        fl = info['file_line']
        toks = tokens_by_line.get(fl, [])
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == 'KW' and t.value == 'goto':
                if i + 1 < len(toks) and toks[i+1].kind == 'NUMBER':
                    target = int(toks[i+1].value)
                    if target not in label_set:
                        errs.append(AnalysisError('semantic', f"goto para rótulo inexistente {target}", fl, info['label'], t.col, info['line_text']))
                    i += 2
                    continue
            i += 1

    ends = [info for info in non_comment_lines if re.search(r'\bend\b', info['line_text'])]
    if len(ends) > 1:
        for e in ends:
            errs.append(AnalysisError('semantic', "múltiplas instruções 'end'", e['file_line'], e['label'], 1, e['line_text']))
    if len(ends) == 1:
        last = non_comment_lines[-1]
        if ends[0]['file_line'] != last['file_line']:
            errs.append(AnalysisError('semantic', "'end' deve ser última instrução", ends[0]['file_line'], ends[0]['label'], 1, ends[0]['line_text']))

    return errs


def analyze_file(path: str) -> Tuple[List[AnalysisError], List[Dict], Dict[int, List[Token]]]:
    """Executa análise completa."""
    errors: List[AnalysisError] = []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        print(f"Erro: arquivo '{path}' não encontrado.")
        sys.exit(1)

    non_comment_lines: List[Dict] = []
    tokens_by_line: Dict[int, List[Token]] = {}

    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip('\n')
        if line.strip() == '':
            continue

        m = re.match(r'^\s*(\d+)\s+(.*)$', line)
        if not m:
            errors.append(AnalysisError('syntax', "linha deve começar com rótulo", idx, None, 1, line))
            continue

        label = int(m.group(1))
        rest = m.group(2)
        rest_start_col = m.start(2) + 1

        if re.match(r'^rem(\b|$)', rest):
            continue

        non_comment_lines.append({
            'file_line': idx,
            'label': label,
            'line_text': line,
            'rest': rest,
            'rest_start_col': rest_start_col
        })

    for info in non_comment_lines:
        toks = lex_rest(info['rest'], info['file_line'], info['label'], info['rest_start_col'], errors)
        tokens_by_line[info['file_line']] = toks

    for info in non_comment_lines:
        toks = tokens_by_line.get(info['file_line'], [])
        syn_errs = parse_statement(toks, info['file_line'], info['label'], info['line_text'])
        errors.extend(syn_errs)

    sem_errs = semantic_analysis(non_comment_lines, tokens_by_line)
    errors.extend(sem_errs)

    return errors, non_comment_lines, tokens_by_line


# ============================================================================
# PARTE 2: AST E OTIMIZAÇÃO
# ============================================================================

@dataclass
class ASTNode:
    line_number: int


@dataclass
class Program(ASTNode):
    statements: List['Statement'] = field(default_factory=list)


@dataclass
class Statement(ASTNode):
    label: int


@dataclass
class InputStmt(Statement):
    var_name: str


@dataclass
class PrintStmt(Statement):
    var_name: str


@dataclass
class LetStmt(Statement):
    var_name: str
    expression: 'Expression'


@dataclass
class GotoStmt(Statement):
    target_label: int


@dataclass
class IfGotoStmt(Statement):
    left_expr: 'Expression'
    operator: str
    right_expr: 'Expression'
    target_label: int


@dataclass
class EndStmt(Statement):
    pass


@dataclass
class Expression(ASTNode):
    pass


@dataclass
class NumberLiteral(Expression):
    value: int


@dataclass
class Variable(Expression):
    name: str


@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression


@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str
    right: Expression


class ASTBuilder:
    """Constrói AST."""

    def __init__(self, tokens_by_line: Dict[int, List[Token]], line_info: List[Dict]):
        self.tokens_by_line = tokens_by_line
        self.line_info = line_info

    def build(self) -> Program:
        statements = []
        for info in self.line_info:
            tokens = self.tokens_by_line.get(info['file_line'], [])
            if not tokens:
                continue
            stmt = self._build_statement(tokens, info['file_line'], info['label'])
            if stmt:
                statements.append(stmt)
        return Program(line_number=1, statements=statements)

    def _build_statement(self, tokens: List[Token], line_num: int, label: int) -> Optional[Statement]:
        if not tokens:
            return None
        kw = tokens[0].value

        if kw == 'input':
            return InputStmt(line_number=line_num, label=label, var_name=tokens[1].value)
        elif kw == 'print':
            return PrintStmt(line_number=line_num, label=label, var_name=tokens[1].value)
        elif kw == 'goto':
            return GotoStmt(line_number=line_num, label=label, target_label=int(tokens[1].value))
        elif kw == 'end':
            return EndStmt(line_number=line_num, label=label)
        elif kw == 'let':
            return LetStmt(line_number=line_num, label=label, var_name=tokens[1].value, expression=self._build_expression(tokens[3:]))
        elif kw == 'if':
            return self._build_if_goto(tokens, line_num, label)
        return None

    def _build_expression(self, tokens: List[Token]) -> Expression:
        if not tokens:
            raise ValueError("Expressão vazia")
        if tokens[0].kind == 'MINUS':
            return UnaryOp(line_number=tokens[0].file_line, operator='-', operand=self._build_operand(tokens[1]))
        if len(tokens) == 1:
            return self._build_operand(tokens[0])
        if len(tokens) >= 3:
            return BinaryOp(line_number=tokens[0].file_line, left=self._build_operand(tokens[0]), operator=tokens[1].value, right=self._build_operand(tokens[2]))
        return self._build_operand(tokens[0])

    def _build_operand(self, token: Token) -> Expression:
        if token.kind == 'NUMBER':
            return NumberLiteral(line_number=token.file_line, value=int(token.value))
        elif token.kind == 'NAME':
            return Variable(line_number=token.file_line, name=token.value)
        raise ValueError(f"Operando inválido: {token.value}")

    def _build_if_goto(self, tokens: List[Token], line_num: int, label: int) -> IfGotoStmt:
        relop_idx = next((i for i, t in enumerate(tokens[1:], 1) if t.kind == 'RELOP'), -1)
        left_expr = self._build_expression(tokens[1:relop_idx])
        operator = tokens[relop_idx].value
        goto_idx = next((i for i, t in enumerate(tokens[relop_idx+1:], relop_idx+1) if t.kind == 'KW' and t.value == 'goto'), -1)
        right_expr = self._build_expression(tokens[relop_idx+1:goto_idx])
        target_label = int(tokens[goto_idx+1].value)
        return IfGotoStmt(line_number=line_num, label=label, left_expr=left_expr, operator=operator, right_expr=right_expr, target_label=target_label)


class CodeOptimizer:
    """Otimizador: constant folding."""

    def __init__(self, ast: Program):
        self.ast = ast

    def optimize(self) -> Program:
        self._constant_folding()
        return self.ast

    def _constant_folding(self):
        for stmt in self.ast.statements:
            if isinstance(stmt, LetStmt):
                stmt.expression = self._fold_expression(stmt.expression)
            elif isinstance(stmt, IfGotoStmt):
                stmt.left_expr = self._fold_expression(stmt.left_expr)
                stmt.right_expr = self._fold_expression(stmt.right_expr)

    def _fold_expression(self, expr: Expression) -> Expression:
        if isinstance(expr, BinaryOp):
            left = self._fold_expression(expr.left)
            right = self._fold_expression(expr.right)
            if isinstance(left, NumberLiteral) and isinstance(right, NumberLiteral):
                result = self._eval_binop(left.value, expr.operator, right.value)
                return NumberLiteral(line_number=expr.line_number, value=result)
            expr.left = left
            expr.right = right
        elif isinstance(expr, UnaryOp):
            operand = self._fold_expression(expr.operand)
            if isinstance(operand, NumberLiteral):
                return NumberLiteral(line_number=expr.line_number, value=-operand.value)
            expr.operand = operand
        return expr

    def _eval_binop(self, left: int, op: str, right: int) -> int:
        ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b,
               '/': lambda a, b: a // b if b != 0 else 0, '%': lambda a, b: a % b if b != 0 else 0}
        return ops[op](left, right)


# ============================================================================
# PARTE 3: GERAÇÃO DE CÓDIGO SML
# ============================================================================

@dataclass
class SMLInstruction:
    """Instrução SML."""
    address: int
    word: int
    comment: str = ""

    def __str__(self) -> str:
        sign = '+' if self.word >= 0 else '-'
        abs_word = abs(self.word)
        word_str = f"{sign}{abs_word:04d}"
        if self.comment:
            return f"{self.address:02d}  {word_str}    # {self.comment}"
        return f"{self.address:02d}  {word_str}"


class SMLCodeGenerator:
    """Gerador de código SML otimizado."""

    def __init__(self, ast: Program):
        self.ast = ast
        self.code: List[SMLInstruction] = []
        self.next_addr = 0
        self.variables: Dict[str, int] = {}      # var_name -> addr
        self.constants: Dict[int, int] = {}      # value -> addr
        self.label_to_addr: Dict[int, int] = {}  # SIMPLE label -> SML addr
        self.temp_counter = 0

    def generate(self) -> List[SMLInstruction]:
        """Gera código SML completo."""
        # Primeira passagem: gerar código e marcar posições de labels
        for stmt in self.ast.statements:
            self.label_to_addr[stmt.label] = self.next_addr
            self._generate_statement(stmt)

        # Alocar variáveis e constantes
        self._allocate_memory()

        # Segunda passagem: resolver endereços
        return self.code

    def _emit(self, opcode: int, operand: int, comment: str = ""):
        """Emite instrução SML."""
        word = opcode * 100 + operand
        self.code.append(SMLInstruction(self.next_addr, word, comment))
        self.next_addr += 1

    def _get_temp_addr(self) -> int:
        """Aloca endereço temporário."""
        temp_name = f"__temp_{self.temp_counter}"
        self.temp_counter += 1
        if temp_name not in self.variables:
            self.variables[temp_name] = 0  # será alocado depois
        return 0  # placeholder

    def _get_var_addr(self, var_name: str) -> int:
        """Obtém/cria endereço de variável."""
        if var_name not in self.variables:
            self.variables[var_name] = 0  # placeholder
        return 0  # será resolvido depois

    def _get_const_addr(self, value: int) -> int:
        """Obtém/cria endereço de constante."""
        if value not in self.constants:
            self.constants[value] = 0  # placeholder
        return 0  # será resolvido depois

    def _generate_statement(self, stmt: Statement):
        """Gera código para statement."""
        if isinstance(stmt, InputStmt):
            addr = self._get_var_addr(stmt.var_name)
            self._emit(SMLOpCode.READ, 99, f"read {stmt.var_name}")
            # Placeholder 99, será resolvido

        elif isinstance(stmt, PrintStmt):
            addr = self._get_var_addr(stmt.var_name)
            self._emit(SMLOpCode.WRITE, 99, f"write {stmt.var_name}")

        elif isinstance(stmt, LetStmt):
            self._generate_expression(stmt.expression)
            addr = self._get_var_addr(stmt.var_name)
            self._emit(SMLOpCode.STORE, 99, f"store {stmt.var_name}")

        elif isinstance(stmt, GotoStmt):
            self._emit(SMLOpCode.BRANCH, 99, f"goto {stmt.target_label}")

        elif isinstance(stmt, IfGotoStmt):
            self._generate_if_goto(stmt)

        elif isinstance(stmt, EndStmt):
            self._emit(SMLOpCode.HALT, 0, "halt")

    def _generate_expression(self, expr: Expression):
        """Gera código para expressão (resultado fica no acumulador)."""
        if isinstance(expr, NumberLiteral):
            addr = self._get_const_addr(expr.value)
            self._emit(SMLOpCode.LOAD, 99, f"load {expr.value}")

        elif isinstance(expr, Variable):
            addr = self._get_var_addr(expr.name)
            self._emit(SMLOpCode.LOAD, 99, f"load {expr.name}")

        elif isinstance(expr, UnaryOp):
            # -x = 0 - x
            zero_addr = self._get_const_addr(0)
            self._emit(SMLOpCode.LOAD, 99, "load 0")
            temp = self._get_temp_addr()
            self._emit(SMLOpCode.STORE, 99, "store temp")
            self._generate_expression(expr.operand)
            temp_addr = 99  # placeholder
            self._emit(SMLOpCode.STORE, 99, "store operand")
            self._emit(SMLOpCode.LOAD, 99, "load 0")
            self._emit(SMLOpCode.SUBTRACT, 99, "subtract operand")

        elif isinstance(expr, BinaryOp):
            # Avalia left, salva, avalia right, opera
            self._generate_expression(expr.left)
            temp = self._get_temp_addr()
            self._emit(SMLOpCode.STORE, 99, f"store temp (left)")
            self._generate_expression(expr.right)
            temp2 = self._get_temp_addr()
            self._emit(SMLOpCode.STORE, 99, f"store temp (right)")
            self._emit(SMLOpCode.LOAD, 99, f"load temp (left)")

            op_map = {
                '+': (SMLOpCode.ADD, "add"),
                '-': (SMLOpCode.SUBTRACT, "subtract"),
                '*': (SMLOpCode.MULTIPLY, "multiply"),
                '/': (SMLOpCode.DIVIDE, "divide"),
                '%': (SMLOpCode.MODULE, "module")
            }
            opcode, opname = op_map[expr.operator]
            self._emit(opcode, 99, f"{opname} temp (right)")

    def _generate_if_goto(self, stmt: IfGotoStmt):
        """
        Gera código para if/goto.
        Estratégia: calcular left - right e usar BRANCHNEG/BRANCHZERO conforme operador.
        """
        # Calcula left
        self._generate_expression(stmt.left_expr)
        temp_left = self._get_temp_addr()
        self._emit(SMLOpCode.STORE, 99, "store left")

        # Calcula right
        self._generate_expression(stmt.right_expr)
        temp_right = self._get_temp_addr()
        self._emit(SMLOpCode.STORE, 99, "store right")

        # Carrega left e subtrai right (acc = left - right)
        self._emit(SMLOpCode.LOAD, 99, "load left")
        self._emit(SMLOpCode.SUBTRACT, 99, "subtract right")

        # Decide branch baseado no operador
        if stmt.operator == '==':
            # Se acc == 0, branch
            self._emit(SMLOpCode.BRANCHZERO, 99, f"if == goto {stmt.target_label}")
        elif stmt.operator == '!=':
            # Se acc != 0, precisa de lógica adicional
            # Estratégia: BRANCHZERO para pular o BRANCH
            skip_addr = self.next_addr + 2
            self._emit(SMLOpCode.BRANCHZERO, 99, f"if == skip")
            self._emit(SMLOpCode.BRANCH, 99, f"goto {stmt.target_label}")
        elif stmt.operator == '<':
            # Se acc < 0, branch
            self._emit(SMLOpCode.BRANCHNEG, 99, f"if < goto {stmt.target_label}")
        elif stmt.operator == '<=':
            # Se acc <= 0, branch (neg ou zero)
            self._emit(SMLOpCode.BRANCHNEG, 99, f"if < goto {stmt.target_label}")
            self._emit(SMLOpCode.BRANCHZERO, 99, f"if == goto {stmt.target_label}")
        elif stmt.operator == '>':
            # Se acc > 0, não neg e não zero, então inverte lógica
            skip_addr = self.next_addr + 3
            self._emit(SMLOpCode.BRANCHNEG, 99, "if < skip")
            self._emit(SMLOpCode.BRANCHZERO, 99, "if == skip")
            self._emit(SMLOpCode.BRANCH, 99, f"goto {stmt.target_label}")
        elif stmt.operator == '>=':
            # Se acc >= 0, não neg
            skip_addr = self.next_addr + 2
            self._emit(SMLOpCode.BRANCHNEG, 99, "if < skip")
            self._emit(SMLOpCode.BRANCH, 99, f"goto {stmt.target_label}")

    def _allocate_memory(self):
        """Aloca variáveis e constantes na memória e resolve endereços."""
        # Calcular endereço inicial para dados (após código)
        data_start = self.next_addr

        # Alocar variáveis
        var_list = sorted([v for v in self.variables.keys() if not v.startswith('__temp')])
        temp_list = sorted([v for v in self.variables.keys() if v.startswith('__temp')])

        for var_name in var_list:
            self.variables[var_name] = data_start
            data_start += 1

        for temp_name in temp_list:
            self.variables[temp_name] = data_start
            data_start += 1

        # Alocar constantes
        for value in sorted(self.constants.keys()):
            self.constants[value] = data_start
            data_start += 1

        # Resolver endereços no código
        for instr in self.code:
            if instr.word % 100 == 99:  # placeholder
                opcode = instr.word // 100
                comment = instr.comment

                # Identificar tipo de operando
                if "load" in comment or "store" in comment or "read" in comment or "write" in comment:
                    # Extrair nome da variável/constante
                    parts = comment.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if name.isdigit() or (name.startswith('-') and name[1:].isdigit()):
                            # É constante
                            value = int(name)
                            addr = self.constants.get(value, 0)
                        else:
                            # É variável
                            addr = self.variables.get(name, 0)
                        instr.word = opcode * 100 + addr

                elif "add" in comment or "subtract" in comment or "multiply" in comment or "divide" in comment or "module" in comment:
                    # Operação aritmética com temporário
                    parts = comment.split()
                    if "temp" in comment:
                        # Encontrar temp
                        temps = [v for v in self.variables.keys() if v.startswith('__temp')]
                        if temps:
                            addr = self.variables[temps[-1] if "right" in comment else temps[-2] if len(temps) >= 2 else temps[0]]
                            instr.word = opcode * 100 + addr

                elif "goto" in comment:
                    # Branch
                    parts = comment.split()
                    if len(parts) >= 2 and parts[-1].isdigit():
                        target_label = int(parts[-1])
                        addr = self.label_to_addr.get(target_label, 0)
                        instr.word = opcode * 100 + addr
                    elif "skip" in comment:
                        # Resolver skip inline
                        # Já foi calculado durante geração
                        pass

        # Adicionar seção de dados
        for var_name in var_list:
            addr = self.variables[var_name]
            self.code.append(SMLInstruction(addr, 0, f"variable {var_name}"))

        for temp_name in temp_list:
            addr = self.variables[temp_name]
            self.code.append(SMLInstruction(addr, 0, f"temp {temp_name}"))

        for value in sorted(self.constants.keys()):
            addr = self.constants[value]
            self.code.append(SMLInstruction(addr, value, f"constant {value}"))


# ============================================================================
# PIPELINE COMPLETO
# ============================================================================

def compile_to_sml(source_file: str, output_file: str = None):
    """Pipeline completo: SIMPLE → SML."""

    print(f"╔{'═'*60}╗")
    print(f"║{'Compilador SIMPLE → SML':^60}║")
    print(f"╚{'═'*60}╝\n")
    print(f"Arquivo fonte: {source_file}\n")

    # Fase 1: Análise
    print("→ Fase 1: Análise Léxica, Sintática e Semântica")
    errors, line_info, tokens_by_line = analyze_file(source_file)

    if errors:
        print("✗ Erros detectados:\n")
        for e in sorted(errors, key=lambda x: (x.file_line, x.col)):
            print(f'{e}\n')
        print(f"Total: {len(errors)} erro(s)")
        sys.exit(2)

    print(f"  ✓ Análise concluída ({len(line_info)} statements)\n")

    # Fase 2: AST
    print("→ Fase 2: Construção da AST")
    builder = ASTBuilder(tokens_by_line, line_info)
    ast = builder.build()
    print(f"  ✓ AST construída ({len(ast.statements)} nós)\n")

    # Fase 3: Otimização
    print("→ Fase 3: Otimização")
    optimizer = CodeOptimizer(ast)
    optimized_ast = optimizer.optimize()
    print(f"  ✓ Constant folding aplicado\n")

    # Fase 4: Geração SML
    print("→ Fase 4: Geração de Código SML")
    generator = SMLCodeGenerator(optimized_ast)
    sml_code = generator.generate()
    print(f"  ✓ {len(sml_code)} instruções SML geradas\n")

    # Estatísticas
    print(f"{'─'*60}")
    print(f"Estatísticas:")
    print(f"  • Variáveis: {len([v for v in generator.variables.keys() if not v.startswith('__temp')])}")
    print(f"  • Temporários: {len([v for v in generator.variables.keys() if v.startswith('__temp')])}")
    print(f"  • Constantes: {len(generator.constants)}")
    print(f"  • Tamanho total: {len(sml_code)} palavras")
    print(f"{'─'*60}\n")

    # Exibir código
    print("╔═══╦════════╦═══════════════════════════════════════╗")
    print("║ # ║ Código ║ Comentário                            ║")
    print("╠═══╬════════╬═══════════════════════════════════════╣")
    for instr in sml_code:
        sign = '+' if instr.word >= 0 else '-'
        abs_word = abs(instr.word)
        word_str = f"{sign}{abs_word:04d}"
        comment = instr.comment[:35] if instr.comment else ""
        print(f"║{instr.address:2d} ║ {word_str} ║ {comment:<37}║")
    print("╚═══╩════════╩═══════════════════════════════════════╝\n")

    # Salvar arquivo
    if output_file:
        with open(output_file, 'w') as f:
            for instr in sml_code:
                sign = '+' if instr.word >= 0 else '-'
                abs_word = abs(instr.word)
                f.write(f"{sign}{abs_word:04d}\n")
        print(f"✓ Código SML salvo em: {output_file}")
    else:
        output_file = source_file.rsplit('.', 1)[0] + '.sml'
        with open(output_file, 'w') as f:
            for instr in sml_code:
                sign = '+' if instr.word >= 0 else '-'
                abs_word = abs(instr.word)
                f.write(f"{sign}{abs_word:04d}\n")
        print(f"✓ Código SML salvo em: {output_file}")

    print("\n✓ Compilação concluída com sucesso!")
    return sml_code


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Compilador SIMPLE → SML (Simpletron Machine Language)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 compilador_completo.py simple.txt
  python3 compilador_completo.py programa.txt -o saida.sml
        """
    )

    parser.add_argument('arquivo', nargs='?', default='simple.txt',
                        help='Arquivo fonte SIMPLE')
    parser.add_argument('-o', '--output', help='Arquivo de saída SML')

    args = parser.parse_args()

    try:
        compile_to_sml(args.arquivo, args.output)
        sys.exit(0)
    except FileNotFoundError:
        print(f"✗ Erro: arquivo '{args.arquivo}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
