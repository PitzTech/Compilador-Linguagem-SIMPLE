"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  COMPILADOR SIMPLE → SML (Simpletron)                        ║
║                                                                              ║
║  Traduz programas SIMPLE para Simpletron Machine Language (SML)             ║
║  com otimizações agressivas para evitar memory overflow                     ║
║                                                                              ║
║  Autor: Victor Laurentino do Nascimento - 2312130047                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Uso:
    python3 compilador.py [arquivo.txt]

Saída:
    binary.txt - Código SML executável no Simpletron
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# CÓDIGOS DE OPERAÇÃO SML (Simpletron Machine Language)
# ═══════════════════════════════════════════════════════════════════════════

class SML:
    """Códigos de operação do Simpletron."""
    # I/O
    READ = 10
    WRITE = 11
    # Load/Store
    LOAD = 20
    STORE = 21
    # Aritmética
    ADD = 30
    SUB = 31
    DIV = 32
    MUL = 33
    MOD = 34
    # Controle
    BRANCH = 40
    BRANCHNEG = 41
    BRANCHZERO = 42
    HALT = 43


# ═══════════════════════════════════════════════════════════════════════════
# ANALISADOR LÉXICO, SINTÁTICO E SEMÂNTICO
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int


@dataclass
class Error:
    phase: str
    msg: str
    line: int
    col: int
    text: str

    def __str__(self):
        return f"[{self.phase.upper()}] Linha {self.line}, col {self.col}: {self.msg}\n  {self.text}\n  {' '*(self.col-1)}^"


TOKEN_SPEC = [
    ('RELOP', r'==|!=|>=|<=|>|<'),
    ('NUM', r'\d+'),
    ('KW', r'rem|input|let|print|goto|if|end'),
    ('VAR', r'[a-z]'),
    ('EQ', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('MOD', r'%'),
    ('WS', r'[ \t]+'),
    ('BAD', r'.'),
]
TOKEN_RE = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC))


def tokenize(code: str, line_num: int, col_offset: int) -> Tuple[List[Token], List[Error]]:
    """Tokeniza uma linha de código."""
    tokens, errors = [], []
    for m in TOKEN_RE.finditer(code):
        kind, val = m.lastgroup, m.group()
        col = col_offset + m.start()
        if kind == 'WS':
            continue
        if kind == 'BAD':
            if val.isupper():
                errors.append(Error('lex', f"maiúscula não permitida: '{val}'", line_num, col, code))
            else:
                errors.append(Error('lex', f"caractere inválido: '{val}'", line_num, col, code))
            continue
        tokens.append(Token(kind, val, line_num, col))
    return tokens, errors


def parse_expr(tokens: List[Token], pos: int, stop: set) -> int:
    """Valida expressão (máx 1 operação binária)."""

    def operand(p):
        if p >= len(tokens):
            raise ValueError("operando esperado")
        t = tokens[p]
        if t.kind == 'MINUS':
            if p+1 >= len(tokens) or tokens[p+1].kind not in ('NUM', 'VAR'):
                raise ValueError("operando esperado após '-'")
            return p+2
        if t.kind in ('NUM', 'VAR'):
            return p+1
        raise ValueError(f"operando inválido: '{t.value}'")

    p = operand(pos)
    if p >= len(tokens) or tokens[p].kind in stop:
        return p
    if tokens[p].kind not in ('PLUS', 'MINUS', 'MUL', 'DIV', 'MOD'):
        return p
    p = operand(p+1)
    if p < len(tokens) and tokens[p].kind not in stop:
        raise ValueError(f"apenas 1 operação permitida, encontrado: '{tokens[p].value}'")
    return p


def parse_stmt(tokens: List[Token], line_num: int, text: str) -> Optional[Error]:
    """Valida sintaxe de statement."""
    if not tokens:
        return Error('syntax', 'instrução vazia', line_num, 1, text)

    kw = tokens[0]
    if kw.kind != 'KW':
        return Error('syntax', f"esperado comando, encontrado '{kw.value}'", line_num, kw.col, text)

    try:
        if kw.value == 'input':
            if len(tokens) != 2 or tokens[1].kind != 'VAR':
                raise ValueError("'input' requer variável")

        elif kw.value == 'print':
            if len(tokens) != 2 or tokens[1].kind != 'VAR':
                raise ValueError("'print' requer variável")

        elif kw.value == 'goto':
            if len(tokens) != 2 or tokens[1].kind != 'NUM':
                raise ValueError("'goto' requer número de linha")

        elif kw.value == 'end':
            if len(tokens) != 1:
                raise ValueError("'end' não aceita argumentos")

        elif kw.value == 'let':
            if len(tokens) < 4 or tokens[1].kind != 'VAR' or tokens[2].kind != 'EQ':
                raise ValueError("formato: let <var> = <expr>")
            if parse_expr(tokens, 3, set()) != len(tokens):
                raise ValueError("expressão inválida")

        elif kw.value == 'if':
            p = parse_expr(tokens, 1, {'RELOP'})
            if p >= len(tokens) or tokens[p].kind != 'RELOP':
                raise ValueError("operador relacional esperado")
            p = parse_expr(tokens, p+1, {'KW'})
            if p >= len(tokens) or tokens[p].value != 'goto':
                raise ValueError("'goto' esperado")
            if p+1 >= len(tokens) or tokens[p+1].kind != 'NUM':
                raise ValueError("número de linha esperado")
            if p+2 != len(tokens):
                raise ValueError("tokens extras")

        return None

    except ValueError as e:
        return Error('syntax', str(e), line_num, kw.col, text)


def analyze(path: str) -> Tuple[List[Error], Dict]:
    """Análise completa: léxica, sintática e semântica."""
    errors = []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"✗ Arquivo '{path}' não encontrado")
        sys.exit(1)

    statements = []

    # Análise léxica e sintática
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip('\n')
        if not line.strip():
            continue

        m = re.match(r'^\s*(\d+)\s+(.*)$', line)
        if not m:
            errors.append(Error('syntax', 'linha deve iniciar com label', i, 1, line))
            continue

        label = int(m.group(1))
        code = m.group(2)
        col_offset = m.start(2) + 1

        # Ignora comentários
        if re.match(r'^rem\b', code):
            continue

        # Tokeniza
        tokens, lex_errors = tokenize(code, i, col_offset)
        errors.extend(lex_errors)
        if lex_errors:
            continue

        # Parse
        err = parse_stmt(tokens, i, line)
        if err:
            errors.append(err)
            continue

        statements.append({
            'label': label,
            'line': i,
            'text': line,
            'tokens': tokens
        })

    if errors:
        return errors, {}

    # Análise semântica
    labels = [s['label'] for s in statements]
    label_set = set(labels)

    # Labels crescentes
    for i in range(1, len(labels)):
        if labels[i] <= labels[i-1]:
            s = statements[i]
            errors.append(Error('semantic', f"label {labels[i]} não cresce após {labels[i-1]}", s['line'], 1, s['text']))

    # Labels únicos
    seen = {}
    for s in statements:
        if s['label'] in seen:
            errors.append(Error('semantic', f"label {s['label']} duplicado", s['line'], 1, s['text']))
        seen[s['label']] = s['line']

    # Gotos válidos
    for s in statements:
        for i, t in enumerate(s['tokens']):
            if t.value == 'goto' and i+1 < len(s['tokens']):
                target = int(s['tokens'][i+1].value)
                if target not in label_set:
                    errors.append(Error('semantic', f"goto para label inexistente: {target}", s['line'], t.col, s['text']))

    # End único e final
    ends = [s for s in statements if any(t.value == 'end' for t in s['tokens'])]
    if len(ends) > 1:
        for e in ends:
            errors.append(Error('semantic', "múltiplos 'end'", e['line'], 1, e['text']))
    if ends and ends[0] != statements[-1]:
        errors.append(Error('semantic', "'end' deve ser último", ends[0]['line'], 1, ends[0]['text']))

    return errors, {'statements': statements, 'labels': label_set}


# ═══════════════════════════════════════════════════════════════════════════
# GERADOR DE CÓDIGO SML OTIMIZADO
# ═══════════════════════════════════════════════════════════════════════════

class SMLGenerator:
    """Gerador de código SML com otimizações agressivas."""

    def __init__(self, data: Dict):
        self.statements = data['statements']
        self.code = []
        self.addr = 0
        self.vars = {}        # var -> addr
        self.consts = {}      # value -> addr
        self.labels = {}      # label -> addr
        self.temps = []       # temp addrs
        self.const_values = {}  # var -> known constant value
        self.var_last_use = {}  # var -> último statement que usa
        self.var_usage = {}     # var -> contador de usos

    def generate(self) -> List[str]:
        """Gera código SML otimizado."""
        # Análise de dataflow para otimizações
        self._analyze_dataflow()

        # Primeira passagem: código
        for stmt in self.statements:
            self.labels[stmt['label']] = self.addr
            self._gen_stmt(stmt)

        # Aloca memória
        self._allocate_memory()

        # Resolve endereços
        self._resolve_addresses()

        return self.code

    def _analyze_dataflow(self):
        """Análise de dataflow para constant propagation e dead code elimination."""
        # Primeira passagem: detecta constantes e último uso
        var_definitions = {}  # var -> idx do statement que define
        var_reads = {}  # var -> lista de statements que leem

        for idx, stmt in enumerate(self.statements):
            tokens = stmt['tokens']
            kw = tokens[0].value

            # Atualiza último uso de variáveis lidas
            if kw == 'print':
                var = tokens[1].value
                self.var_last_use[var] = idx
                self.var_usage[var] = self.var_usage.get(var, 0) + 1
                if var not in var_reads:
                    var_reads[var] = []
                var_reads[var].append(idx)

            elif kw == 'input':
                var = tokens[1].value
                self.const_values[var] = None  # Input invalida constante
                self.var_last_use[var] = idx
                self.var_usage[var] = self.var_usage.get(var, 0) + 1
                var_definitions[var] = idx

            elif kw == 'let':
                var = tokens[1].value
                expr = tokens[3:]

                # Marca variáveis usadas na expressão
                for t in expr:
                    if t.kind == 'VAR':
                        self.var_last_use[t.value] = idx
                        self.var_usage[t.value] = self.var_usage.get(t.value, 0) + 1
                        if t.value not in var_reads:
                            var_reads[t.value] = []
                        var_reads[t.value].append(idx)

                # Tenta propagar constante
                const_val = self._try_eval_constant(expr)
                if const_val is not None:
                    self.const_values[var] = const_val
                else:
                    self.const_values[var] = None

                var_definitions[var] = idx
                self.var_usage[var] = self.var_usage.get(var, 0) + 1

            elif kw == 'if':
                # Marca variáveis usadas no if
                for t in tokens[1:]:
                    if t.kind == 'VAR':
                        self.var_last_use[t.value] = idx
                        self.var_usage[t.value] = self.var_usage.get(t.value, 0) + 1
                        if t.value not in var_reads:
                            var_reads[t.value] = []
                        var_reads[t.value].append(idx)

        # Segunda passagem: determina quais variáveis realmente precisam ser armazenadas
        self.needs_storage = {}
        for var in var_definitions.keys():
            # Variável precisa de storage se:
            # 1. Recebe input (não é constante conhecida)
            # 2. É lida mais de uma vez
            # 3. É lida em um statement não-consecutivo
            # 4. Não tem valor constante conhecido

            if var not in self.const_values or self.const_values[var] is None:
                # Não é constante - precisa de storage
                self.needs_storage[var] = True
            elif var in var_reads:
                reads = var_reads[var]
                def_idx = var_definitions[var]

                # Se tem mais de uma leitura, ou leitura não consecutiva, precisa storage
                if len(reads) > 1 or (len(reads) == 1 and reads[0] != def_idx + 1):
                    self.needs_storage[var] = True
                else:
                    self.needs_storage[var] = False
            else:
                # Nunca é lida - não precisa storage (dead code)
                self.needs_storage[var] = False

    def _try_eval_constant(self, tokens: List[Token]) -> Optional[int]:
        """Tenta avaliar expressão como constante."""
        # Unário: -x
        if tokens[0].kind == 'MINUS':
            if len(tokens) >= 2 and tokens[1].kind == 'NUM':
                return -int(tokens[1].value)
            elif len(tokens) >= 2 and tokens[1].kind == 'VAR':
                var = tokens[1].value
                if var in self.const_values and self.const_values[var] is not None:
                    return -self.const_values[var]
            return None

        # Único operando
        if len(tokens) == 1:
            if tokens[0].kind == 'NUM':
                return int(tokens[0].value)
            elif tokens[0].kind == 'VAR':
                var = tokens[0].value
                if var in self.const_values:
                    return self.const_values[var]
            return None

        # Binário: a op b
        if len(tokens) == 3:
            left, op, right = tokens[0], tokens[1], tokens[2]

            # Obtém valores
            left_val = None
            if left.kind == 'NUM':
                left_val = int(left.value)
            elif left.kind == 'VAR' and left.value in self.const_values:
                left_val = self.const_values[left.value]

            right_val = None
            if right.kind == 'NUM':
                right_val = int(right.value)
            elif right.kind == 'VAR' and right.value in self.const_values:
                right_val = self.const_values[right.value]

            if left_val is None or right_val is None:
                return None

            # Avalia
            if op.value == '+':
                return left_val + right_val
            elif op.value == '-':
                return left_val - right_val
            elif op.value == '*':
                return left_val * right_val
            elif op.value == '/' and right_val != 0:
                return left_val // right_val
            elif op.value == '%' and right_val != 0:
                return left_val % right_val

        return None

    def _emit(self, op: int, operand: int, comment: str = ""):
        """Emite instrução SML."""
        word = op * 100 + operand
        self.code.append({'addr': self.addr, 'word': word, 'comment': comment, 'resolved': operand != 99})
        self.addr += 1

    def _get_var(self, name: str) -> int:
        """Obtém endereço de variável."""
        if name not in self.vars:
            self.vars[name] = 99  # placeholder
        return 99

    def _get_const(self, value: int) -> int:
        """Obtém endereço de constante."""
        if value not in self.consts:
            self.consts[value] = 99
        return 99

    def _get_temp(self) -> int:
        """Aloca temporário."""
        self.temps.append(99)
        return 99

    def _gen_stmt(self, stmt: Dict):
        """Gera código para statement."""
        tokens = stmt['tokens']
        kw = tokens[0].value

        if kw == 'input':
            var = tokens[1].value
            self._get_var(var)
            self._emit(SML.READ, 99, f"read {var}")

        elif kw == 'print':
            var = tokens[1].value

            # Se variável é constante, carrega constante e imprime direto do acumulador
            if var in self.const_values and self.const_values[var] is not None:
                const_val = self.const_values[var]
                self._get_const(const_val)
                self._emit(SML.LOAD, 99, f"load {const_val}")
                # Usa um temporário para imprimir
                temp = self._get_temp()
                self._emit(SML.STORE, 99, f"store temp")
                self._emit(SML.WRITE, 99, f"write temp")
            else:
                self._get_var(var)
                self._emit(SML.WRITE, 99, f"write {var}")

        elif kw == 'let':
            var = tokens[1].value
            self._gen_expr(tokens[3:])

            # Só gera STORE se a variável precisa de storage
            if self.needs_storage.get(var, True):
                self._get_var(var)
                self._emit(SML.STORE, 99, f"store {var}")

        elif kw == 'goto':
            target = int(tokens[1].value)
            self._emit(SML.BRANCH, 99, f"goto {target}")

        elif kw == 'if':
            self._gen_if(tokens, stmt['label'])

        elif kw == 'end':
            self._emit(SML.HALT, 0, "halt")

    def _gen_expr(self, tokens: List[Token]):
        """Gera código para expressão (resultado no acumulador)."""
        # Tenta avaliar como constante primeiro
        const_val = self._try_eval_constant(tokens)
        if const_val is not None:
            # Expressão é constante - carrega diretamente
            self._get_const(const_val)
            self._emit(SML.LOAD, 99, f"load {const_val}")
            return

        # Unário: -x
        if tokens[0].kind == 'MINUS':
            operand = tokens[1]
            self._get_const(0)
            self._emit(SML.LOAD, 99, "load 0")

            if operand.kind == 'NUM':
                self._get_const(int(operand.value))
                self._emit(SML.SUB, 99, f"sub {operand.value}")
            else:
                # Tenta substituir por constante
                if operand.value in self.const_values and self.const_values[operand.value] is not None:
                    val = self.const_values[operand.value]
                    self._get_const(val)
                    self._emit(SML.SUB, 99, f"sub {val}")
                else:
                    self._get_var(operand.value)
                    self._emit(SML.SUB, 99, f"sub {operand.value}")
            return

        # Único operando
        if len(tokens) == 1:
            t = tokens[0]
            if t.kind == 'NUM':
                self._get_const(int(t.value))
                self._emit(SML.LOAD, 99, f"load {t.value}")
            else:
                # Tenta substituir por constante
                if t.value in self.const_values and self.const_values[t.value] is not None:
                    val = self.const_values[t.value]
                    self._get_const(val)
                    self._emit(SML.LOAD, 99, f"load {val}")
                else:
                    self._get_var(t.value)
                    self._emit(SML.LOAD, 99, f"load {t.value}")
            return

        # Binário: a op b
        left, op, right = tokens[0], tokens[1], tokens[2]

        # Carrega left (tenta usar constante se possível)
        if left.kind == 'NUM':
            self._get_const(int(left.value))
            self._emit(SML.LOAD, 99, f"load {left.value}")
        elif left.value in self.const_values and self.const_values[left.value] is not None:
            val = self.const_values[left.value]
            self._get_const(val)
            self._emit(SML.LOAD, 99, f"load {val}")
        else:
            self._get_var(left.value)
            self._emit(SML.LOAD, 99, f"load {left.value}")

        # Opera com right (tenta usar constante se possível)
        if right.kind == 'NUM':
            self._get_const(int(right.value))
            rval = right.value
        elif right.value in self.const_values and self.const_values[right.value] is not None:
            val = self.const_values[right.value]
            self._get_const(val)
            rval = str(val)
        else:
            self._get_var(right.value)
            rval = right.value

        op_map = {'+': SML.ADD, '-': SML.SUB, '*': SML.MUL, '/': SML.DIV, '%': SML.MOD}
        op_name = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod'}
        self._emit(op_map[op.value], 99, f"{op_name[op.value]} {rval}")

    def _gen_if(self, tokens: List[Token], label: int):
        """Gera código para if/goto (OTIMIZADO)."""
        # Encontra RELOP
        relop_idx = next(i for i, t in enumerate(tokens) if t.kind == 'RELOP')
        goto_idx = next(i for i, t in enumerate(tokens) if t.value == 'goto')

        left_tokens = tokens[1:relop_idx]
        relop = tokens[relop_idx].value
        right_tokens = tokens[relop_idx+1:goto_idx]
        target = int(tokens[goto_idx+1].value)

        # Avalia left
        self._gen_expr(left_tokens)
        temp = self._get_temp()
        self._emit(SML.STORE, 99, "store temp_left")

        # Avalia right
        self._gen_expr(right_tokens)
        temp = self._get_temp()
        self._emit(SML.STORE, 99, "store temp_right")

        # Carrega left e subtrai right (acc = left - right)
        self._emit(SML.LOAD, 99, "load temp_left")
        self._emit(SML.SUB, 99, "sub temp_right")

        # Branch otimizado baseado no operador
        if relop == '==':
            self._emit(SML.BRANCHZERO, 99, f"if == goto {target}")

        elif relop == '!=':
            # Se zero, pula; senão, vai
            skip = self.addr + 2
            self._emit(SML.BRANCHZERO, skip, "if == skip")
            self._emit(SML.BRANCH, 99, f"goto {target}")

        elif relop == '<':
            self._emit(SML.BRANCHNEG, 99, f"if < goto {target}")

        elif relop == '<=':
            # Se neg ou zero, vai
            self._emit(SML.BRANCHNEG, 99, f"if < goto {target}")
            self._emit(SML.BRANCHZERO, 99, f"if == goto {target}")

        elif relop == '>':
            # Se não neg e não zero, vai
            skip = self.addr + 3
            self._emit(SML.BRANCHNEG, skip, "if < skip")
            self._emit(SML.BRANCHZERO, skip, "if == skip")
            self._emit(SML.BRANCH, 99, f"goto {target}")

        elif relop == '>=':
            # Se não neg, vai
            skip = self.addr + 2
            self._emit(SML.BRANCHNEG, skip, "if < skip")
            self._emit(SML.BRANCH, 99, f"goto {target}")

    def _allocate_memory(self):
        """Aloca variáveis, constantes e temporários (OTIMIZADO)."""
        data_start = self.addr

        # Filtra variáveis que realmente precisam ser alocadas
        # usando a análise de needs_storage
        vars_to_allocate = {}
        for var in self.vars.keys():
            # Aloca apenas se precisa de storage ou não foi analisada
            if self.needs_storage.get(var, True):
                vars_to_allocate[var] = data_start
                self.code.append({'addr': data_start, 'word': 0, 'comment': f"var {var}", 'resolved': True})
                data_start += 1

        self.vars = vars_to_allocate

        # Temporários (reutiliza slots)
        temp_addr = data_start
        for i in range(min(len(self.temps), 2)):  # Máximo 2 temporários
            self.temps[i] = temp_addr
            self.code.append({'addr': temp_addr, 'word': 0, 'comment': f"temp", 'resolved': True})
            temp_addr += 1
        data_start = temp_addr

        # Constantes (compartilha valores duplicados)
        const_map = {}  # valor -> endereço
        for val in sorted(set(self.consts.keys())):
            if val not in const_map:
                const_map[val] = data_start
                self.code.append({'addr': data_start, 'word': val, 'comment': f"const {val}", 'resolved': True})
                data_start += 1

        # Atualiza todas as referências para o mesmo endereço
        for val in self.consts.keys():
            self.consts[val] = const_map[val]

        # Verificação de overflow
        if data_start > 99:
            print(f"✗ MEMORY OVERFLOW: {data_start} palavras necessárias (máx: 100)")
            sys.exit(1)

    def _resolve_addresses(self):
        """Resolve placeholders (99) para endereços reais."""
        for instr in self.code:
            if instr['resolved']:
                continue

            word = instr['word']
            opcode = word // 100
            comment = instr['comment']
            addr = 0

            # READ/WRITE: busca variável
            if opcode in (SML.READ, SML.WRITE):
                parts = comment.split()
                if len(parts) >= 2:
                    var_name = parts[1]
                    addr = self.vars.get(var_name, 0)

            # STORE: busca variável ou temporário
            elif opcode == SML.STORE:
                if 'temp' in comment:
                    if 'left' in comment:
                        addr = self.temps[0] if self.temps else 0
                    elif 'right' in comment:
                        addr = self.temps[1] if len(self.temps) > 1 else self.temps[0] if self.temps else 0
                    else:
                        addr = self.temps[0] if self.temps else 0
                else:
                    parts = comment.split()
                    if len(parts) >= 2:
                        var_name = parts[1]
                        addr = self.vars.get(var_name, 0)

            # LOAD: busca variável, constante ou temporário
            elif opcode == SML.LOAD:
                if 'temp' in comment:
                    if 'left' in comment:
                        addr = self.temps[0] if self.temps else 0
                    elif 'right' in comment:
                        addr = self.temps[1] if len(self.temps) > 1 else self.temps[0] if self.temps else 0
                    else:
                        addr = self.temps[0] if self.temps else 0
                else:
                    parts = comment.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if name.lstrip('-').isdigit():
                            val = int(name)
                            addr = self.consts.get(val, 0)
                        else:
                            addr = self.vars.get(name, 0)

            # Operações aritméticas: busca variável, constante ou temp
            elif opcode in (SML.ADD, SML.SUB, SML.MUL, SML.DIV, SML.MOD):
                if 'temp' in comment:
                    if 'left' in comment:
                        addr = self.temps[0] if self.temps else 0
                    elif 'right' in comment:
                        addr = self.temps[1] if len(self.temps) > 1 else self.temps[0] if self.temps else 0
                    else:
                        addr = self.temps[0] if self.temps else 0
                else:
                    parts = comment.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if name.lstrip('-').isdigit():
                            val = int(name)
                            addr = self.consts.get(val, 0)
                        else:
                            addr = self.vars.get(name, 0)

            # BRANCH: busca label
            elif opcode in (SML.BRANCH, SML.BRANCHNEG, SML.BRANCHZERO):
                if 'skip' in comment:
                    addr = word % 100  # Já está resolvido
                else:
                    parts = comment.split()
                    for part in parts:
                        if part.isdigit():
                            target_label = int(part)
                            addr = self.labels.get(target_label, word % 100)
                            break

            instr['word'] = opcode * 100 + addr
            instr['resolved'] = True


# ═══════════════════════════════════════════════════════════════════════════
# COMPILADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def compile_simple(source_file: str):
    """Compila SIMPLE → SML."""

    print("╔" + "═" * 78 + "╗")
    print(f"║{'COMPILADOR SIMPLE → SML':^78}║")
    print("╚" + "═" * 78 + "╝\n")
    print(f"Arquivo fonte: {source_file}\n")

    # Fase 1: Análise
    print("→ FASE 1: Análise (Léxica, Sintática, Semântica)")
    errors, data = analyze(source_file)

    if errors:
        print(f"✗ {len(errors)} erro(s) encontrado(s):\n")
        for e in errors:
            print(f"{e}\n")
        sys.exit(2)

    print(f"  ✓ {len(data['statements'])} statements analisados")
    print(f"  ✓ {len(data['labels'])} labels válidos\n")

    # Fase 2: Geração de código
    print("→ FASE 2: Geração de Código SML Otimizado")
    gen = SMLGenerator(data)
    code = gen.generate()

    n_instrs = len([c for c in code if '# ' not in c['comment'] or 'var' not in c['comment']])
    n_vars = len(gen.vars)
    n_temps = len(set(gen.temps))
    n_consts = len(gen.consts)
    total = len(code)

    print(f"  ✓ {n_instrs} instruções geradas")
    print(f"  ✓ {n_vars} variáveis alocadas")
    print(f"  ✓ {n_temps} temporários alocados")
    print(f"  ✓ {n_consts} constantes alocadas")
    print(f"  ✓ {total}/100 palavras usadas ({total}%)\n")

    # Estatísticas de otimização
    print("→ OTIMIZAÇÕES APLICADAS:")
    print("  ✓ Constant folding em expressões")
    print("  ✓ Reutilização de registradores temporários")
    print("  ✓ Eliminação de instruções redundantes")
    print(f"  ✓ Taxa de uso de memória: {total}%\n")

    # Exibe código
    print("╔════╦══════════╦════════════════════════════════════════════════════╗")
    print("║ ## ║  CÓDIGO  ║ COMENTÁRIO                                         ║")
    print("╠════╬══════════╬════════════════════════════════════════════════════╣")
    for instr in code:
        word = instr['word']
        sign = '+' if word >= 0 else '-'
        abs_word = abs(word)
        word_str = f"{sign}{abs_word:04d}"
        comment = instr['comment'][:52]
        print(f"║ {instr['addr']:2d} ║ {word_str} ║ {comment:<54} ║")
    print("╚════╩══════════╩════════════════════════════════════════════════════╝\n")

    # Salva binary.txt
    with open('binary.txt', 'w') as f:
        for instr in code:
            word = instr['word']
            sign = '+' if word >= 0 else '-'
            f.write(f"{sign}{abs(word):04d}\n")

    print("✓ Código SML salvo em: binary.txt")
    print("✓ Compilação concluída com sucesso!\n")


# ═══════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Compilador SIMPLE → SML (Simpletron Machine Language)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('arquivo', nargs='?', default='simple.txt', help='Arquivo fonte SIMPLE')

    args = parser.parse_args()

    try:
        compile_simple(args.arquivo)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n✗ Compilação cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
