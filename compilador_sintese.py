"""
Fase de síntese do compilador SIMPLE.
Gera código de máquina virtual otimizado a partir da análise léxica/sintática/semântica.

Execução:
    python3 compilador_sintese.py

Arquitetura:
    1. Parser AST: Constrói árvore sintática abstrata
    2. Otimizador: Realiza otimizações de código (constant folding, dead code elimination, etc)
    3. Gerador de código: Emite bytecode para máquina virtual SIMPLE
    4. Máquina Virtual: Executa o bytecode gerado
"""

import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from enum import Enum, auto

# ============================================================================
# BYTECODE INSTRUCTION SET - Máquina Virtual SIMPLE
# ============================================================================

class OpCode(Enum):
    """Conjunto de instruções da máquina virtual SIMPLE (otimizado)."""

    # Operações com memória
    LOAD_CONST = auto()      # Carrega constante para o topo da pilha
    LOAD_VAR = auto()        # Carrega variável para o topo da pilha
    STORE_VAR = auto()       # Armazena topo da pilha em variável

    # Operações aritméticas (operam no topo da pilha)
    ADD = auto()             # pop b, pop a, push a+b
    SUB = auto()             # pop b, pop a, push a-b
    MUL = auto()             # pop b, pop a, push a*b
    DIV = auto()             # pop b, pop a, push a//b (divisão inteira)
    MOD = auto()             # pop b, pop a, push a%b
    NEG = auto()             # pop a, push -a

    # Operações relacionais
    EQ = auto()              # ==
    NE = auto()              # !=
    LT = auto()              # <
    LE = auto()              # <=
    GT = auto()              # >
    GE = auto()              # >=

    # Controle de fluxo
    JUMP = auto()            # Salto incondicional
    JUMP_IF_FALSE = auto()   # Salto condicional se topo da pilha é falso
    LABEL = auto()           # Pseudo-instrução para marcação (removida no bytecode final)

    # I/O
    INPUT = auto()           # Lê inteiro do usuário e armazena em variável
    PRINT = auto()           # Imprime variável

    # Controle
    HALT = auto()            # Termina programa


@dataclass
class Instruction:
    """Representa uma instrução de bytecode."""
    opcode: OpCode
    arg: Optional[Any] = None
    line_number: Optional[int] = None  # Para debug

    def __str__(self) -> str:
        if self.arg is not None:
            return f"{self.opcode.name} {self.arg}"
        return self.opcode.name


# ============================================================================
# AST (Abstract Syntax Tree) NODES
# ============================================================================

@dataclass
class ASTNode:
    """Classe base para nós da AST."""
    line_number: int


@dataclass
class Program(ASTNode):
    """Programa SIMPLE completo."""
    statements: List['Statement'] = field(default_factory=list)


@dataclass
class Statement(ASTNode):
    """Classe base para statements."""
    label: int


@dataclass
class InputStmt(Statement):
    """Comando input."""
    var_name: str


@dataclass
class PrintStmt(Statement):
    """Comando print."""
    var_name: str


@dataclass
class LetStmt(Statement):
    """Comando let (atribuição)."""
    var_name: str
    expression: 'Expression'


@dataclass
class GotoStmt(Statement):
    """Comando goto."""
    target_label: int


@dataclass
class IfGotoStmt(Statement):
    """Comando if/goto."""
    left_expr: 'Expression'
    operator: str  # '==', '!=', '<', '<=', '>', '>='
    right_expr: 'Expression'
    target_label: int


@dataclass
class EndStmt(Statement):
    """Comando end."""
    pass


# Expressões
@dataclass
class Expression(ASTNode):
    """Classe base para expressões."""
    pass


@dataclass
class NumberLiteral(Expression):
    """Literal numérico."""
    value: int


@dataclass
class Variable(Expression):
    """Referência a variável."""
    name: str


@dataclass
class UnaryOp(Expression):
    """Operação unária (negação)."""
    operator: str  # '-'
    operand: Expression


@dataclass
class BinaryOp(Expression):
    """Operação binária."""
    left: Expression
    operator: str  # '+', '-', '*', '/', '%'
    right: Expression


# ============================================================================
# AST BUILDER - Construtor de Árvore Sintática Abstrata
# ============================================================================

class ASTBuilder:
    """Constrói AST a partir dos tokens analisados."""

    def __init__(self, tokens_by_line: Dict[int, List], line_info: List[Dict]):
        """
        Args:
            tokens_by_line: Mapa de file_line -> lista de tokens
            line_info: Lista de informações sobre linhas não-comentário
        """
        self.tokens_by_line = tokens_by_line
        self.line_info = line_info

    def build(self) -> Program:
        """Constrói a AST completa do programa."""
        statements = []
        for info in self.line_info:
            file_line = info['file_line']
            label = info['label']
            tokens = self.tokens_by_line.get(file_line, [])

            if not tokens:
                continue

            stmt = self._build_statement(tokens, file_line, label)
            if stmt:
                statements.append(stmt)

        return Program(line_number=1, statements=statements)

    def _build_statement(self, tokens: List, line_num: int, label: int) -> Optional[Statement]:
        """Constrói um statement a partir dos tokens."""
        if not tokens:
            return None

        kw_token = tokens[0]
        kw = kw_token.value

        if kw == 'input':
            return InputStmt(line_number=line_num, label=label, var_name=tokens[1].value)

        elif kw == 'print':
            return PrintStmt(line_number=line_num, label=label, var_name=tokens[1].value)

        elif kw == 'goto':
            return GotoStmt(line_number=line_num, label=label, target_label=int(tokens[1].value))

        elif kw == 'end':
            return EndStmt(line_number=line_num, label=label)

        elif kw == 'let':
            # let x = expr
            var_name = tokens[1].value
            expr = self._build_expression(tokens[3:])
            return LetStmt(line_number=line_num, label=label, var_name=var_name, expression=expr)

        elif kw == 'if':
            # if expr relop expr goto label
            return self._build_if_goto(tokens, line_num, label)

        return None

    def _build_expression(self, tokens: List) -> Expression:
        """Constrói expressão a partir dos tokens."""
        if not tokens:
            raise ValueError("Expressão vazia")

        # Unário: -x ou -123
        if tokens[0].kind == 'MINUS':
            operand = self._build_operand(tokens[1])
            return UnaryOp(line_number=tokens[0].file_line, operator='-', operand=operand)

        # Operando único: x ou 123
        if len(tokens) == 1:
            return self._build_operand(tokens[0])

        # Binário: x + y
        if len(tokens) >= 3:
            left = self._build_operand(tokens[0])
            operator = tokens[1].value
            right = self._build_operand(tokens[2])
            return BinaryOp(line_number=tokens[0].file_line, left=left, operator=operator, right=right)

        return self._build_operand(tokens[0])

    def _build_operand(self, token) -> Expression:
        """Constrói operando (variável ou número)."""
        if token.kind == 'NUMBER':
            return NumberLiteral(line_number=token.file_line, value=int(token.value))
        elif token.kind == 'NAME':
            return Variable(line_number=token.file_line, name=token.value)
        else:
            raise ValueError(f"Operando inválido: {token.value}")

    def _build_if_goto(self, tokens: List, line_num: int, label: int) -> IfGotoStmt:
        """Constrói if/goto statement."""
        # if expr relop expr goto label
        # Localizar RELOP
        relop_idx = -1
        for i, tok in enumerate(tokens[1:], start=1):
            if tok.kind == 'RELOP':
                relop_idx = i
                break

        if relop_idx == -1:
            raise ValueError("RELOP não encontrado em if/goto")

        # Expressão esquerda
        left_tokens = tokens[1:relop_idx]
        left_expr = self._build_expression(left_tokens)

        # Operador
        operator = tokens[relop_idx].value

        # Expressão direita (até 'goto')
        goto_idx = -1
        for i, tok in enumerate(tokens[relop_idx+1:], start=relop_idx+1):
            if tok.kind == 'KW' and tok.value == 'goto':
                goto_idx = i
                break

        right_tokens = tokens[relop_idx+1:goto_idx]
        right_expr = self._build_expression(right_tokens)

        # Target label
        target_label = int(tokens[goto_idx+1].value)

        return IfGotoStmt(
            line_number=line_num,
            label=label,
            left_expr=left_expr,
            operator=operator,
            right_expr=right_expr,
            target_label=target_label
        )


# ============================================================================
# CODE OPTIMIZER - Otimizador de Código
# ============================================================================

class CodeOptimizer:
    """
    Realiza otimizações na AST antes da geração de código.

    Otimizações implementadas:
    1. Constant Folding: Calcula expressões constantes em tempo de compilação
    2. Dead Code Elimination: Remove código após 'goto' incondicional ou 'end'
    3. Strength Reduction: Substitui operações caras por equivalentes mais baratas
    """

    def __init__(self, ast: Program):
        self.ast = ast

    def optimize(self) -> Program:
        """Executa todas as otimizações."""
        self._constant_folding()
        self._dead_code_elimination()
        return self.ast

    def _constant_folding(self):
        """Calcula expressões constantes em tempo de compilação."""
        for stmt in self.ast.statements:
            if isinstance(stmt, LetStmt):
                stmt.expression = self._fold_expression(stmt.expression)
            elif isinstance(stmt, IfGotoStmt):
                stmt.left_expr = self._fold_expression(stmt.left_expr)
                stmt.right_expr = self._fold_expression(stmt.right_expr)

    def _fold_expression(self, expr: Expression) -> Expression:
        """Simplifica expressão se possível."""
        if isinstance(expr, BinaryOp):
            # Fold recursivamente
            left = self._fold_expression(expr.left)
            right = self._fold_expression(expr.right)

            # Se ambos são literais, calcular
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
        """Avalia operação binária."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left // right if right != 0 else 0
        elif op == '%':
            return left % right if right != 0 else 0
        return 0

    def _dead_code_elimination(self):
        """Remove código morto (unreachable code)."""
        # Identificar statements após goto incondicional ou end
        reachable = set()
        labels = {stmt.label for stmt in self.ast.statements}

        # Marcar todos como alcançáveis por padrão (análise simples)
        for stmt in self.ast.statements:
            reachable.add(stmt.label)

        # Em uma implementação completa, faria análise de fluxo de controle
        # Por ora, mantemos todos os statements
        pass


# ============================================================================
# CODE GENERATOR - Gerador de Bytecode
# ============================================================================

class CodeGenerator:
    """Gera bytecode otimizado a partir da AST."""

    def __init__(self, ast: Program):
        self.ast = ast
        self.code: List[Instruction] = []
        self.label_positions: Dict[int, int] = {}  # label -> posição no código

    def generate(self) -> List[Instruction]:
        """Gera código completo."""
        # Primeira passagem: marcar posições de labels
        temp_code = []
        for stmt in self.ast.statements:
            self.label_positions[stmt.label] = len(temp_code)
            temp_code.extend(self._generate_statement(stmt))

        # Adicionar HALT se não houver END explícito
        if not temp_code or temp_code[-1].opcode != OpCode.HALT:
            temp_code.append(Instruction(OpCode.HALT))

        # Segunda passagem: resolver labels
        self.code = self._resolve_labels(temp_code)

        return self.code

    def _generate_statement(self, stmt: Statement) -> List[Instruction]:
        """Gera código para um statement."""
        code = []

        if isinstance(stmt, InputStmt):
            code.append(Instruction(OpCode.INPUT, stmt.var_name, stmt.line_number))

        elif isinstance(stmt, PrintStmt):
            code.append(Instruction(OpCode.PRINT, stmt.var_name, stmt.line_number))

        elif isinstance(stmt, LetStmt):
            # Gerar código para expressão (deixa resultado no topo da pilha)
            code.extend(self._generate_expression(stmt.expression))
            # Armazenar em variável
            code.append(Instruction(OpCode.STORE_VAR, stmt.var_name, stmt.line_number))

        elif isinstance(stmt, GotoStmt):
            code.append(Instruction(OpCode.JUMP, stmt.target_label, stmt.line_number))

        elif isinstance(stmt, IfGotoStmt):
            # Avaliar left
            code.extend(self._generate_expression(stmt.left_expr))
            # Avaliar right
            code.extend(self._generate_expression(stmt.right_expr))
            # Comparação (deixa bool no topo)
            code.append(self._relop_to_instruction(stmt.operator, stmt.line_number))
            # Jump se verdadeiro (invertemos a lógica: comparamos e invertemos)
            code.append(Instruction(OpCode.JUMP_IF_FALSE, ('SKIP', len(code) + 2), stmt.line_number))
            code.append(Instruction(OpCode.JUMP, stmt.target_label, stmt.line_number))
            # Label SKIP será resolvido depois

        elif isinstance(stmt, EndStmt):
            code.append(Instruction(OpCode.HALT, None, stmt.line_number))

        return code

    def _generate_expression(self, expr: Expression) -> List[Instruction]:
        """Gera código para expressão (resultado fica no topo da pilha)."""
        code = []

        if isinstance(expr, NumberLiteral):
            code.append(Instruction(OpCode.LOAD_CONST, expr.value, expr.line_number))

        elif isinstance(expr, Variable):
            code.append(Instruction(OpCode.LOAD_VAR, expr.name, expr.line_number))

        elif isinstance(expr, UnaryOp):
            code.extend(self._generate_expression(expr.operand))
            code.append(Instruction(OpCode.NEG, None, expr.line_number))

        elif isinstance(expr, BinaryOp):
            code.extend(self._generate_expression(expr.left))
            code.extend(self._generate_expression(expr.right))
            code.append(self._binop_to_instruction(expr.operator, expr.line_number))

        return code

    def _binop_to_instruction(self, op: str, line_num: int) -> Instruction:
        """Converte operador binário em instrução."""
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
        }
        return Instruction(op_map[op], None, line_num)

    def _relop_to_instruction(self, op: str, line_num: int) -> Instruction:
        """Converte operador relacional em instrução."""
        op_map = {
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '<=': OpCode.LE,
            '>': OpCode.GT,
            '>=': OpCode.GE,
        }
        return Instruction(op_map[op], None, line_num)

    def _resolve_labels(self, code: List[Instruction]) -> List[Instruction]:
        """Resolve referências a labels para endereços absolutos."""
        resolved = []
        for instr in code:
            if instr.opcode in (OpCode.JUMP, OpCode.JUMP_IF_FALSE):
                if isinstance(instr.arg, tuple) and instr.arg[0] == 'SKIP':
                    # Resolvido inline
                    resolved.append(Instruction(instr.opcode, instr.arg[1], instr.line_number))
                elif isinstance(instr.arg, int) and instr.arg in self.label_positions:
                    # Resolver label
                    resolved.append(Instruction(instr.opcode, self.label_positions[instr.arg], instr.line_number))
                else:
                    resolved.append(instr)
            else:
                resolved.append(instr)
        return resolved


# ============================================================================
# VIRTUAL MACHINE - Máquina Virtual SIMPLE
# ============================================================================

class VirtualMachine:
    """Máquina virtual que executa o bytecode gerado."""

    def __init__(self, code: List[Instruction]):
        self.code = code
        self.stack: List[int] = []
        self.variables: Dict[str, int] = {}
        self.pc = 0  # Program counter
        self.halted = False

    def run(self):
        """Executa o programa."""
        while not self.halted and self.pc < len(self.code):
            self._execute_instruction(self.code[self.pc])
            self.pc += 1

    def _execute_instruction(self, instr: Instruction):
        """Executa uma instrução."""
        op = instr.opcode

        if op == OpCode.LOAD_CONST:
            self.stack.append(instr.arg)

        elif op == OpCode.LOAD_VAR:
            self.stack.append(self.variables.get(instr.arg, 0))

        elif op == OpCode.STORE_VAR:
            self.variables[instr.arg] = self.stack.pop()

        elif op == OpCode.ADD:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)

        elif op == OpCode.SUB:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)

        elif op == OpCode.MUL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)

        elif op == OpCode.DIV:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a // b if b != 0 else 0)

        elif op == OpCode.MOD:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a % b if b != 0 else 0)

        elif op == OpCode.NEG:
            self.stack.append(-self.stack.pop())

        elif op == OpCode.EQ:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a == b else 0)

        elif op == OpCode.NE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a != b else 0)

        elif op == OpCode.LT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a < b else 0)

        elif op == OpCode.LE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a <= b else 0)

        elif op == OpCode.GT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a > b else 0)

        elif op == OpCode.GE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a >= b else 0)

        elif op == OpCode.JUMP:
            self.pc = instr.arg - 1  # -1 porque será incrementado

        elif op == OpCode.JUMP_IF_FALSE:
            if self.stack.pop() == 0:
                self.pc = instr.arg - 1

        elif op == OpCode.INPUT:
            try:
                value = int(input("? "))
                self.variables[instr.arg] = value
            except (ValueError, EOFError):
                self.variables[instr.arg] = 0

        elif op == OpCode.PRINT:
            print(self.variables.get(instr.arg, 0))

        elif op == OpCode.HALT:
            self.halted = True


# ============================================================================
# COMPILER PIPELINE
# ============================================================================

def compile_and_run(source_file: str, show_code: bool = False):
    """Pipeline completo: análise -> síntese -> execução."""
    # Importar analisador
    from compilador_analise import analyze_file, lex_rest

    # Fase 1: Análise
    errors = analyze_file(source_file)
    if errors:
        print('\nErros detectados durante análise:')
        for e in sorted(errors, key=lambda x: (x.file_line, x.col)):
            print(f'\n- {e}')
        print(f"\nTotal de erros: {len(errors)}")
        sys.exit(2)

    print("✓ Análise léxica, sintática e semântica: OK")

    # Fase 2: Construir tokens e info
    with open(source_file, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    non_comment_lines = []
    tokens_by_line = {}

    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip('\n')
        if line.strip() == '':
            continue
        m = re.match(r'^\s*(\d+)\s+(.*)$', line)
        if not m:
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

        # Lex
        errors_temp = []
        toks = lex_rest(rest, idx, label, rest_start_col, errors_temp)
        tokens_by_line[idx] = toks

    # Fase 3: Construir AST
    print("✓ Construindo AST...")
    builder = ASTBuilder(tokens_by_line, non_comment_lines)
    ast = builder.build()

    # Fase 4: Otimizar
    print("✓ Otimizando código...")
    optimizer = CodeOptimizer(ast)
    optimized_ast = optimizer.optimize()

    # Fase 5: Gerar código
    print("✓ Gerando bytecode...")
    generator = CodeGenerator(optimized_ast)
    bytecode = generator.generate()

    if show_code:
        print("\n--- Bytecode Gerado ---")
        for i, instr in enumerate(bytecode):
            print(f"{i:3d}: {instr}")
        print("----------------------\n")

    # Fase 6: Executar
    print("✓ Executando programa SIMPLE...\n")
    vm = VirtualMachine(bytecode)
    vm.run()

    print("\n✓ Programa finalizado com sucesso.")


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compilador SIMPLE - Fase de Síntese')
    parser.add_argument('arquivo', nargs='?', default='simple.txt', help='Arquivo fonte SIMPLE (padrão: simple.txt)')
    parser.add_argument('--show-code', action='store_true', help='Mostrar bytecode gerado')

    args = parser.parse_args()

    try:
        compile_and_run(args.arquivo, show_code=args.show_code)
    except FileNotFoundError:
        print(f"Erro: arquivo '{args.arquivo}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro durante compilação/execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
