"""
Analisador (léxico, sintático e semântico) para a linguagem SIMPLE.
Coloque o código em `simple.txt` (mesma pasta) e rode:
    python3 simple_compiler.py
Retornos:
    0 = nenhum erro
    2 = erros encontrados
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict

# ---------------- Data classes ----------------
@dataclass
class Token:
    kind: str
    value: str
    file_line: int    # 1-based line index in file
    label: Optional[int]  # numeric label of the line (None for comment/blank)
    col: int          # 1-based column where token starts

@dataclass
class AnalysisError:
    phase: str    # 'lex', 'syntax', 'semantic'
    message: str
    file_line: int
    label: Optional[int]
    col: int
    line_text: str

    def __str__(self) -> str:
        lbl = f" rótulo={self.label}" if self.label is not None else ""
        header = f"[{self.phase.upper()}] linha {self.file_line}{lbl} coluna {self.col}: {self.message}"
        # caret line: show the source line and a caret under the column
        caret_pos = max(1, min(self.col, len(self.line_text) + 1))
        caret_line = self.line_text + "\n" + (" " * (caret_pos - 1)) + "^"
        return header + "\n  " + caret_line

# ---------------- Lexer specification ----------------
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
    ('MISMATCH',r'.'),
]
_MASTER_RE = re.compile('|'.join(f"(?P<{n}>{p})" for n, p in TOKEN_SPECS))

def lex_rest(rest: str, file_line: int, label: Optional[int], rest_start_col: int, errors: List[AnalysisError]) -> List[Token]:
    """Tokeniza a parte após o rótulo. Registra erros léxicos com coluna precisa."""
    tokens: List[Token] = []
    pos = 0
    L = len(rest)
    while pos < L:
        m = _MASTER_RE.match(rest, pos)
        if not m:
            # should not occur, but safety
            errors.append(AnalysisError('lex', 'caractere inválido', file_line, label, rest_start_col + pos, rest))
            break
        kind = m.lastgroup
        val = m.group()
        start = m.start()
        col = rest_start_col + start  # 1-based column in full line
        if kind == 'WS':
            pos = m.end()
            continue
        if kind == 'MISMATCH':
            ch = val
            if ch.isalpha() and ch.upper() == ch:
                # uppercase letter outside comment
                errors.append(AnalysisError('lex', f"letra maiúscula não permitida fora de comentário: '{ch}'", file_line, label, col, rest))
            else:
                errors.append(AnalysisError('lex', f"token inválido: '{ch}'", file_line, label, col, rest))
            pos = m.end()
            continue
        # normal token
        tokens.append(Token(kind, val, file_line, label, col))
        pos = m.end()
    return tokens

# ---------------- Parser helpers ----------------
class ParserError(Exception):
    def __init__(self, message: str, file_line: int, label: Optional[int], col: int):
        super().__init__(message)
        self.message = message
        self.file_line = file_line
        self.label = label
        self.col = col

# precedence for binary ops
BIN_OPS_PRECEDENCE = {
    'PLUS': 10,
    'MINUS': 10,
    'MUL': 20,
    'DIV': 20,
    'MOD': 20,
}

def parse_expression(tokens: List[Token], pos: int, file_line: int, label: Optional[int], stop_kinds: Optional[set] = None) -> int:
    """Parser de expressão para SIMPLE: no máximo 1 operação binária."""
    if stop_kinds is None:
        stop_kinds = set()

    def parse_operand(p: int) -> int:
        if p >= len(tokens):
            last_col = tokens[-1].col if tokens else 1
            raise ParserError('expressão incompleta: operando esperado', file_line, label, last_col)
        t = tokens[p]
        if t.kind == 'MINUS':
            # unário: -x ou -123
            if p + 1 >= len(tokens):
                raise ParserError("operando esperado após '-'", file_line, label, t.col)
            if tokens[p+1].kind not in ('NUMBER', 'NAME'):
                raise ParserError("após '-' só pode vir número ou variável", file_line, label, tokens[p+1].col)
            return p + 2
        if t.kind in ('NUMBER', 'NAME'):
            return p + 1
        raise ParserError(f"operando inválido '{t.value}'", file_line, label, t.col)

    # primeiro operando
    p = parse_operand(pos)

    # se não tem operador binário, terminou
    if p >= len(tokens) or tokens[p].kind in stop_kinds:
        return p

    # se tem operador binário, consome
    if tokens[p].kind not in ('PLUS', 'MINUS', 'MUL', 'DIV', 'MOD'):
        return p  # fim da expressão, outro token (como RELOP ou KW)
    op_tok = tokens[p]
    p += 1

    # segundo operando obrigatório
    p = parse_operand(p)

    # agora NÃO pode haver mais nada, exceto stop_kinds
    if p < len(tokens) and tokens[p].kind not in stop_kinds:
        raise ParserError(f"apenas uma operação é permitida por expressão; encontrado '{tokens[p].value}'", file_line, label, tokens[p].col)

    return p

def parse_statement(tokens: List[Token], file_line: int, label: Optional[int], line_text: str) -> List[AnalysisError]:
    errs: List[AnalysisError] = []
    if not tokens:
        errs.append(AnalysisError('syntax', 'instrução ausente após rótulo', file_line, label, 1, line_text))
        return errs
    first = tokens[0]
    if first.kind != 'KW':
        errs.append(AnalysisError('syntax', f"esperada instrução (rem/input/let/print/goto/if/end), encontrada '{first.value}'", file_line, label, first.col, line_text))
        return errs
    kw = first.value
    try:
        if kw == 'input':
            if len(tokens) < 2:
                raise ParserError("'input' requer uma variável", file_line, label, first.col + len(first.value))
            t = tokens[1]
            if t.kind != 'NAME':
                raise ParserError("'input' requer uma variável (uma letra minúscula)", file_line, label, t.col)
            if len(tokens) != 2:
                extra = tokens[2]
                raise ParserError(f"token extra após 'input': '{extra.value}'", file_line, label, extra.col)

        elif kw == 'print':
            if len(tokens) < 2:
                raise ParserError("'print' requer uma variável", file_line, label, first.col + len(first.value))
            t = tokens[1]
            if t.kind != 'NAME':
                raise ParserError("'print' só aceita variável (uma letra minúscula)", file_line, label, t.col)
            if len(tokens) != 2:
                extra = tokens[2]
                raise ParserError(f"token extra após 'print': '{extra.value}'", file_line, label, extra.col)

        elif kw == 'goto':
            if len(tokens) < 2:
                raise ParserError("'goto' requer número de linha", file_line, label, first.col + len(first.value))
            t = tokens[1]
            if t.kind != 'NUMBER':
                raise ParserError("'goto' requer número de linha (literal)", file_line, label, t.col)
            if len(tokens) != 2:
                extra = tokens[2]
                raise ParserError(f"token extra após 'goto': '{extra.value}'", file_line, label, extra.col)

        elif kw == 'end':
            if len(tokens) != 1:
                extra = tokens[1]
                raise ParserError("'end' não aceita argumentos", file_line, label, extra.col)

        elif kw == 'let':
            if len(tokens) < 4:
                raise ParserError("uso: let <var> = <expressão>", file_line, label, first.col)
            name_tok = tokens[1]
            if name_tok.kind != 'NAME':
                raise ParserError("nome de variável inválido na atribuição (esperada uma letra minúscula)", file_line, label, name_tok.col)
            assign_tok = tokens[2]
            if assign_tok.kind != 'ASSIGN':
                raise ParserError("esperado '=' após variável em 'let'", file_line, label, assign_tok.col)
            endpos = parse_expression(tokens, 3, file_line, label, stop_kinds=set())
            if endpos != len(tokens):
                extra = tokens[endpos]
                raise ParserError(f"token extra após expressão em 'let': '{extra.value}'", file_line, label, extra.col)

        elif kw == 'if':
            pos_after_left = parse_expression(tokens, 1, file_line, label, stop_kinds={'RELOP'})
            if pos_after_left >= len(tokens) or tokens[pos_after_left].kind != 'RELOP':
                col = tokens[pos_after_left].col if pos_after_left < len(tokens) else (tokens[-1].col if tokens else 1)
                raise ParserError("operador relacional esperado (==, !=, >, >=, <, <=)", file_line, label, col)
            pos = pos_after_left + 1
            pos_after_right = parse_expression(tokens, pos, file_line, label, stop_kinds={'KW'})
            if pos_after_right >= len(tokens) or not (tokens[pos_after_right].kind == 'KW' and tokens[pos_after_right].value == 'goto'):
                col = tokens[pos_after_right].col if pos_after_right < len(tokens) else (tokens[-1].col if tokens else 1)
                raise ParserError("depois da condição do if só pode vir 'goto'", file_line, label, col)
            if pos_after_right + 1 >= len(tokens):
                raise ParserError("'goto' deve ser seguido por número de linha", file_line, label, tokens[pos_after_right].col)
            num_tok = tokens[pos_after_right + 1]
            if num_tok.kind != 'NUMBER':
                raise ParserError("'goto' deve ser seguido por número de linha literal", file_line, label, num_tok.col)
            if pos_after_right + 2 != len(tokens):
                extra = tokens[pos_after_right + 2]
                raise ParserError(f"token extra após if/goto: '{extra.value}'", file_line, label, extra.col)

        else:
            raise ParserError(f"instrução desconhecida '{kw}'", file_line, label, first.col)

    except ParserError as pe:
        errs.append(AnalysisError('syntax', pe.message, pe.file_line, pe.label, pe.col, line_text))
    return errs

# ---------------- Semantic checks ----------------
def semantic_analysis(non_comment_lines: List[Dict], tokens_by_line: Dict[int, List[Token]]) -> List[AnalysisError]:
    errs: List[AnalysisError] = []
    if not non_comment_lines:
        return errs
    labels = [info['label'] for info in non_comment_lines]
    # strictly increasing
    for i in range(1, len(labels)):
        if labels[i] <= labels[i-1]:
            info = non_comment_lines[i]
            errs.append(AnalysisError('semantic', f"rótulos não estão estritamente crescentes: {labels[i-1]} seguido de {labels[i]}", info['file_line'], info['label'], 1, info['line_text']))
    # duplicates
    seen = {}
    for info in non_comment_lines:
        lbl = info['label']
        if lbl in seen:
            errs.append(AnalysisError('semantic', f"rótulo duplicado {lbl} (aparece na linha {seen[lbl]} e {info['file_line']})", info['file_line'], lbl, 1, info['line_text']))
        else:
            seen[lbl] = info['file_line']
    label_set = set(labels)
    # check goto targets
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
                else:
                    errs.append(AnalysisError('semantic', "'goto' não seguido por número de linha", fl, info['label'], t.col, info['line_text']))
            i += 1
    # end rules: at most one end and if present must be last non-comment line
    ends = [info for info in non_comment_lines if re.search(r'\\bend\\b', info['line_text'])]
    if len(ends) > 1:
        for e in ends:
            errs.append(AnalysisError('semantic', "múltiplas instruções 'end' encontradas", e['file_line'], e['label'], 1, e['line_text']))
    if len(ends) == 1:
        last = non_comment_lines[-1]
        if ends[0]['file_line'] != last['file_line']:
            errs.append(AnalysisError('semantic', "'end' deve ser a última instrução executável (não comentário)", ends[0]['file_line'], ends[0]['label'], 1, ends[0]['line_text']))

    return errs

# ---------------- Pipeline ----------------
def analyze_file(path: str) -> List[AnalysisError]:
    errors: List[AnalysisError] = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        print(f"Erro: arquivo '{path}' não encontrado.")
        sys.exit(1)

    non_comment_lines: List[Dict] = []  # executable lines only
    tokens_by_line: Dict[int, List[Token]] = {}

    # scan and separate comments (completely ignored)
    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip('\n')
        if line.strip() == '':
            continue
        m = re.match(r'^\s*(\d+)\s+(.*)$', line)
        if not m:
            errors.append(AnalysisError('syntax', "linha deve começar com número de rótulo seguido por instrução", idx, None, 1, line))
            continue
        label = int(m.group(1))
        rest = m.group(2)
        rest_start_col = m.start(2) + 1
        # comment line (exact 'rem' token in lowercase)
        if re.match(r'^rem(\b|$)', rest):
            continue
        non_comment_lines.append({'file_line': idx, 'label': label, 'line_text': line, 'rest': rest, 'rest_start_col': rest_start_col})

    # lexical
    for info in non_comment_lines:
        fl = info['file_line']
        lbl = info['label']
        rest = info['rest']
        base_col = info['rest_start_col']
        toks = lex_rest(rest, fl, lbl, base_col, errors)
        tokens_by_line[fl] = toks

    # syntax
    for info in non_comment_lines:
        fl = info['file_line']
        lbl = info['label']
        toks = tokens_by_line.get(fl, [])
        syn_errs = parse_statement(toks, fl, lbl, info['line_text'])
        errors.extend(syn_errs)

    # semantic (run even if earlier errors exist, to show more)
    sem_errs = semantic_analysis(non_comment_lines, tokens_by_line)
    errors.extend(sem_errs)

    return errors

# ---------------- CLI ----------------
if __name__ == '__main__':
    path = 'simple.txt'
    errs = analyze_file(path)
    if errs:
        errs_sorted = sorted(errs, key=lambda e: (e.file_line, e.col))
        print('\nErros detectados:')
        for e in errs_sorted:
            print('\n- ', e)
        print(f"\nTotal de erros: {len(errs_sorted)}")
        sys.exit(2)
    else:
        print('\nNenhum erro encontrado. Análise léxica, sintática e semântica: OK.')
        sys.exit(0)
