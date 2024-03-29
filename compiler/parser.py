import sys

from working_with_syntax_tree import WorkingWithSyntaxTree
from constant import Constant
from variable import Variable
from lexer import Lexer
from typing import List, Tuple

def print_tree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.children:
        print_tree(child, depth + 1)


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Parser(WorkingWithSyntaxTree):
    class ParserError(Exception):
        def __init__(self, message: str, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

        def __str__(self) -> str:
            return f"{self.message} ({self.line}:{self.index})"

    class CompoundParserError(ParserError):
        def __init__(self, main_msg: str, line: int, index: int, messages: tuple, errors: tuple):
            final_msg = main_msg + f" ({line}:{index})\n"
            for i in range(len(messages)):
                final_msg += f"{messages[i]}: {errors[i]}\n"

            super().__init__(final_msg, line, index)

        def __str__(self) -> str:
            return self.message

    class Expected(ParserError):
        def __init__(self, expected: str, line: int, index: int):
            super().__init__(f"{expected} expected", line, index)

    class Unexpected(ParserError):
        def __init__(self, what_is_unexpected: str, line: int, index: int):
            super().__init__(f"unexpected {what_is_unexpected}", line, index)

    class CannotCompare(ParserError):
        def __init__(self, line: int, index: int):
            super().__init__("cannot compare string and number", line, index)

    class DoubleDeclaration(ParserError):
        def __init__(self, name: str, line: int, index: int):
            super().__init__(f"double declaration of {name}", line, index)

    class UsingOfNotDeclared(ParserError):
        def __init__(self, name: str, line: int, index: int):
            super().__init__(f"using not declared variable {name}", line, index)

    class InvalidVarType(ParserError):
        def __init__(self, tp: str, expected_type: str, line: int, index: int):
            super().__init__(f"{tp} variable cannot be used in this expression ({expected_type} expected)", line, index)

    class ForbiddenStatement(ParserError):
        def __init__(self, stmt: str, line: int, index: int):
            super().__init__(f"{stmt} cannot be used in this block", line, index)

    class ArrayInitializationError(ParserError):
        def __init__(self, line: int, index: int):
            super().__init__(f"cannot initialize array", line, index)

    class ArrSizeLessThan1(ParserError):
        def __init__(self, line: int, index: int):
            super().__init__(f"array size must be > 0", line, index)

    class IncorrectNumOfIndexes(ParserError):
        def __init__(self, line: int, index: int):
            super().__init__(f"incorrect amount of indexes", line, index)

    class Node(Lexer.Token):
        def __init__(self, tbl = None, index_in_tbl = None, children = None, line: int = 0, index: int = 0):
            if children is None:
                children = []

            self.children = children

            super().__init__(tbl, index_in_tbl, line, index)

        def __str__(self):
            return str(self.table[self.index_in_table])

    def __init__(self, tokens: List[Lexer.Token], ops_tbl, idents_tbl, keywords_tbl, consts_tbl):
        super().__init__(
            ["program", "declare", "compound_statement", "indexation"],
            ops_tbl,
            idents_tbl,
            keywords_tbl,
            consts_tbl,
            None
        )

        self._tokens = tokens
        self._current_token_index = 0
        # self._switch_expression_type = None  # None if we are not parsing switch, type if we are.
        self._switch_expression_types = []
        # self._inside_of_loop = False
        self._num_loops = 0

        self._current_level = 0
        self._blocks_on_levels = [1]
        self._scope_stack = [(0, 1)]

    def get_parser_nodes(self) -> list:
        return self._parser_nodes_tbl

    def _go_to_next_tok(self):
        self._current_token_index += 1

    def _no_more_tokens(self):
        return self._current_token_index >= len(self._tokens)

    def _curr_tok(self) -> Lexer.Token:
        if self._no_more_tokens():
            tok = self._tokens[len(self._tokens) - 1]
            line = tok.line
            index = tok.index + len(tok.table[tok.index_in_table])
            raise Parser.Unexpected("end of file", line, index)

        return self._tokens[self._current_token_index]

    def print_syntax_tree(self):
        print_tree(self._syntax_tree)

    def _match_number(self, tok: Lexer.Token):
        """Check that this token is a number."""
        # if tok.table is not self._consts_tbl or not is_number(tok.table[tok.index_in_table]):
        if tok.table is not self._consts_tbl or tok.value().type not in (Constant.DOUBLE, Constant.INT):
            raise Parser.Expected("number", tok.line, tok.index)

    def _match_string(self, tok: Lexer.Token):
        """Check that this token is a string"""
        if tok.table is not self._consts_tbl or tok.value().type != Constant.STRING:
            raise Parser.Expected("string", tok.line, tok.index)

    def _match_operator(self, tok: Lexer.Token, op: [str, tuple]):
        if not self._is_operator(tok, op):
            raise Parser.Expected(str(op), tok.line, tok.index)

    def _match_identifier(self, tok: Lexer.Token):
        # if tok.table is not self._idents_tbl:
        if not self._is_identifier(tok):
            raise Parser.Expected("identifier", tok.line, tok.index)

    def _match_identifier_of_type(self, tok: Lexer.Token, type: [str, tuple]):
        if not self._is_identifier_of_type(tok, type):
            raise Parser.Expected(f"{type} variable", tok.line, tok.index)

    def _match_keyword(self, tok: Lexer.Token, keyword: [str, tuple]):
        if not self._is_keyword(tok, keyword):
            raise Parser.Expected(str(keyword), tok.line, tok.index)

    def _match_bool_literal(self, tok: Lexer.Token):
        if tok.table is not self._keywords_tbl or tok.value() not in ("true", "false"):
            raise Parser.Expected("boolean literal", tok.line, tok.index)

    def _match_var_type(self, tok: Lexer.Token, tp: [str, tuple]):
        actual_type = tok.value().type[0] if isinstance(tok.value().type, list) else tok.value().type

        if isinstance(tp, tuple):
            # if tok.value().type not in tp:
            if actual_type not in tp:
                raise Parser.InvalidVarType(actual_type, str(tp), tok.line, tok.index)
        else:
            # if tok.value().type != tp:
            if actual_type != tp:
                raise Parser.InvalidVarType(actual_type, tp, tok.line, tok.index)

    def _check_for_forbidden_statements(self, tok: Lexer.Token):
        # if self._switch_expression_type is None:
        if len(self._switch_expression_types) < 1:
            if self._is_keyword(tok, ("case", "default")):
                raise Parser.ForbiddenStatement(tok.value(), tok.line, tok.index)
            # if self._is_keyword(tok, "break") and not self._inside_of_loop:
            if self._is_keyword(tok, "break") and self._num_loops < 1:
                raise Parser.ForbiddenStatement(tok.value(), tok.line, tok.index)

    def _parse_operator(self, op: str) -> Node:
        tok = self._curr_tok()
        self._match_operator(tok, op)
        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_non_negative_int_literal(self) -> Node:
        tok = self._curr_tok()

        if not (tok.table is self._consts_tbl and tok.value().type == Constant.INT):
            raise Parser.Expected("non-negative int literal", tok.line, tok.index)

        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_identifier_in_declaration(self, type_node: Node) -> Node:
        tok = self._curr_tok()
        self._match_identifier(tok)
        self._go_to_next_tok()
        arr_sizes = []

        while self._is_operator(self._curr_tok(), '['):
            self._go_to_next_tok()
            curr_size_node = self._parse_non_negative_int_literal()
            arr_size = int(curr_size_node.value().value)

            if arr_size < 1:
                raise Parser.ArrSizeLessThan1(curr_size_node.line, curr_size_node.index)

            arr_sizes.append(arr_size)
            self._match_operator(self._curr_tok(), ']')
            self._go_to_next_tok()

        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)

        curr_block = self._scope_stack[len(self._scope_stack) - 1]  # 0 - level, 1 - number of block

        if ret.value().type is not None:
            for var in self._idents_tbl:
                if ret.value().name == var.name and curr_block[0] == var.nest_level and curr_block[1] == var.block_on_level:
                    raise Parser.DoubleDeclaration(ret.value().name, ret.line, ret.index)

            # it is a new variable with the same name. add it to the table
            self._idents_tbl.append(Variable(ret.value().name, None, 0, 0))
            ret.index_in_table = len(self._idents_tbl) - 1

        if len(arr_sizes) < 1:
            ret.table[ret.index_in_table].type = type_node.value()
        else:
            ret.table[ret.index_in_table].type = [type_node.value()] + arr_sizes
        ret.table[ret.index_in_table].nest_level = curr_block[0]
        ret.table[ret.index_in_table].block_on_level = curr_block[1]

        return ret

    def _parse_identifier_in_using(self, type = None) -> Node:
        tok = self._curr_tok()
        self._match_identifier(tok)
        self._go_to_next_tok()

        if type is not None and tok.value().type is not None:
            # if not isinstance(tok.value().type, list):
            self._match_var_type(tok, type)

        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)

        if ret.value().type is None:
            raise Parser.UsingOfNotDeclared(ret.value().name, ret.line, ret.index)

        scope_stack_index = len(self._scope_stack) - 1
        var_real_index = -1

        while scope_stack_index >= 0:
            curr_block = self._scope_stack[scope_stack_index]
            searched_var = Variable(ret.value().name, ret.value().type, curr_block[0], curr_block[1])

            try:
                var_real_index = self._idents_tbl.index(searched_var)
                break
            except ValueError:
                scope_stack_index -= 1

        if var_real_index < 0:
            raise Parser.UsingOfNotDeclared(ret.value().name, ret.line, ret.index)

        ret.index_in_table = var_real_index
        return ret

    def _parse_identifier_in_using_or_indexation(self, type = None) -> Node:
        ident_node = self._parse_identifier_in_using(type)
        var_type = ident_node.value().type
        min_indexes_num = 0
        max_indexes_num = 0

        if not isinstance(var_type, list) and var_type != "string":
            return ident_node

        if var_type == "string":
            max_indexes_num = 1
        else:
            # this is an array
            min_indexes_num = len(var_type) - 1
            max_indexes_num = min_indexes_num
            if var_type[0] == "string":
                max_indexes_num += 1

        # num_indexes = len(var_type) - 1
        indexes = []
        while self._is_operator(self._curr_tok(), '['):
            self._go_to_next_tok()
            indexes.append(self._parse_arithmetic_expression())
            self._match_operator(self._curr_tok(), ']')
            self._go_to_next_tok()
        # for i in range(num_indexes):
        #     self._match_operator(self._curr_tok(), '[')
        #     self._go_to_next_tok()
        #
        #     indexes.append(self._parse_arithmetic_expression())
        #
        #     self._match_operator(self._curr_tok(), ']')
        #     self._go_to_next_tok()

        if len(indexes) < min_indexes_num or len(indexes) > max_indexes_num:
            raise Parser.IncorrectNumOfIndexes(ident_node.line, ident_node.index)

        if len(indexes) < 1:
            return ident_node

        indexation_node = Parser.Node(
            self._parser_nodes_tbl,
            self._parser_nodes_tbl.index("indexation"),
            line=ident_node.line,
            index=ident_node.index
        )
        indexation_node.children = [ident_node] + indexes
        return indexation_node

    def _parse_atoifb(self):
        tok = self._curr_tok()
        if tok.table is not self._keywords_tbl or tok.value() not in ("atoi", "atof", "atob"):
            raise Parser.Expected("atoi, atof or atob", tok.line, tok.index)

        op = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), '(')
        self._go_to_next_tok()
        string = self._parse_string_expression()
        self._match_operator(self._curr_tok(), ')')
        self._go_to_next_tok()

        op.children = [string]
        return op

    def _parse_factor(self) -> Node:
        tok = self._curr_tok()

        if tok.table is self._idents_tbl:
            # ret = self._parse_identifier_in_using(("int", "double"))
            ret = self._parse_identifier_in_using_or_indexation(("int", "double"))
        elif tok.table is self._ops_tbl and tok.value() == '(':
            self._go_to_next_tok()
            ret = self._parse_arithmetic_expression()
            self._match_operator(self._curr_tok(), ')')
            self._go_to_next_tok()
        elif tok.table is self._keywords_tbl and tok.value() in ("atoi", "atof"):
            ret = self._parse_atoifb()
        # elif tok.table is self._consts_tbl and tok.value().type in (Constant.DOUBLE, Constant.INT):
        else:
            self._match_number(tok)
            ret = Parser.Node(self._consts_tbl, tok.index_in_table, None, tok.line, tok.index)
            self._go_to_next_tok()

        return ret

    def _parse_term(self) -> Node:
        num1 = self._parse_factor()

        while not self._no_more_tokens() and self._is_mulop(self._curr_tok()):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            num2 = self._parse_factor()
            op.children = [num1, num2]
            num1 = op

        return num1

    def _parse_signed_term(self) -> Node:
        tok = self._curr_tok()
        sign = None
        if self._is_addop(tok):
            sign = self._parse_operator(tok.value())

        term = self._parse_term()

        if sign is None:
            return term

        sign.children = [term]
        return sign

    def _parse_arithmetic_expression(self) -> Node:
        term1 = self._parse_signed_term()

        while not self._no_more_tokens() and self._is_addop(self._curr_tok()):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            term2 = self._parse_term()
            op.children = [term1, term2]
            term1 = op

        return term1

    def _parse_bool_arithm_or_string_expr(self) -> Tuple[Node, str]:
        old_tok = self._curr_tok()
        old_token_index = self._current_token_index

        try:
            ret = self._parse_bool_expression()
            return ret, "bool"
        except Parser.ParserError as err1:
            self._current_token_index = old_token_index
            try:
                ret = self._parse_arithmetic_expression()
                return ret, "arithmetic"
            except Parser.ParserError as err2:
                self._current_token_index = old_token_index
                try:
                    ret = self._parse_string_expression()
                    return ret, "string"
                except Parser.ParserError as err3:
                    raise Parser.CompoundParserError(
                        "this expression is not a valid string, arithmetic or boolean expression",
                        old_tok.line, old_tok.index,
                        ("invalid boolean expression", "invalid arithmetic expression", "invalid string expression"),
                        (err1, err2, err3)
                    )
                    # raise Parser.Expected("valid boolean, arithmetic or string expression", old_tok.line, old_tok.index)

    def _parse_to_string(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "to_string")
        op = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)

        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), '(')
        self._go_to_next_tok()

        expr, _ = self._parse_bool_arithm_or_string_expr()
        self._match_operator(self._curr_tok(), ')')
        self._go_to_next_tok()

        op.children = [expr]
        return op

    def _parse_scan(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "scan")
        op = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)

        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), '(')
        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), ')')
        self._go_to_next_tok()
        return op

    def _parse_str_term(self) -> Node:
        tok = self._curr_tok()

        if tok.table is self._idents_tbl:
            # ret = self._parse_identifier()
            # self._match_var_was_declared(ret)
            # ret = self._parse_identifier_in_using("string")
            ret = self._parse_identifier_in_using_or_indexation("string")
            # self._match_var_type(ret, "string")
        elif self._is_keyword(tok, "to_string"):
            ret = self._parse_to_string()
        elif self._is_keyword(tok, "scan"):
            ret = self._parse_scan()
        else:
            self._match_string(tok)
            ret = Parser.Node(self._consts_tbl, tok.index_in_table, None, tok.line, tok.index)
            self._go_to_next_tok()

        return ret

    def _parse_string_expression(self) -> Node:
        term1 = self._parse_str_term()

        while not self._no_more_tokens() and \
                self._curr_tok().table is self._ops_tbl and \
                self._curr_tok().value() == '+':

            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            term2 = self._parse_str_term()
            op.children = [term1, term2]
            term1 = op

        return term1

    def _parse_comp_term(self) -> Tuple[Node, str]:
        return self._parse_arithmetic_or_string_expression("error while parsing comparison part")

    def _parse_switch_expression(self) -> Tuple[Node, str]:
        return self._parse_arithmetic_or_string_expression("error while parsing switch expression")

    def _parse_arithmetic_or_string_expression(self, possible_err_msg: str) -> Tuple[Node, str]:
        old_tok = self._curr_tok()
        old_token_index = self._current_token_index

        try:
            ret = self._parse_arithmetic_expression()
            return ret, "arithmetic"
        except Parser.ParserError as err1:
            self._current_token_index = old_token_index
            try:
                ret = self._parse_string_expression()
                return ret, "string"
            except Parser.ParserError as err2:
                raise Parser.CompoundParserError(
                    possible_err_msg, old_tok.line, old_tok.index,
                    ("invalid arithmetic expression", "invalid string expression"),
                    (err1, err2)
                )

    def _parse_comparison(self) -> Node:
        comp_term1, kind1 = self._parse_comp_term()
        tok = self._curr_tok()
        self._match_operator(tok, ('==', '!=', '>=', '<=', '>', '<'))
        comp_op = self._parse_operator(tok.value())

        comp_term2, kind2 = self._parse_comp_term()

        if kind1 != kind2:
            raise Parser.CannotCompare(comp_op.line, comp_op.index)

        comp_op.children = [comp_term1, comp_term2]
        return comp_op

    def _parse_bool_literal(self) -> Node:
        tok = self._curr_tok()
        self._match_bool_literal(tok)
        ret = Parser.Node(self._keywords_tbl, tok.index_in_table, None, tok.line, tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_bool_factor(self) -> Node:
        tok = self._curr_tok()

        if self._is_keyword(tok, "atob"):
            ret = self._parse_atoifb()
        elif tok.table is self._idents_tbl and tok.value().type == "bool":
            # ret = self._parse_identifier_in_using("bool")
            ret = self._parse_identifier_in_using_or_indexation("bool")
        elif self._is_operator(tok, '('):
            # it can be a bool expression. or it can be a part of a comparison.
            old_tok_index = self._current_token_index

            self._go_to_next_tok()

            try:
                ret = self._parse_bool_expression()
                self._match_operator(self._curr_tok(), ')')
                self._go_to_next_tok()
            except Parser.ParserError:
                self._current_token_index = old_tok_index
                ret = self._parse_comparison()
        elif self._is_keyword(tok, ("true", "false")):
            # it is a bool LITERAL.
            ret = self._parse_bool_literal()
        else:
            # it is a comparison
            ret = self._parse_comparison()

        return ret

    def _parse_not_bool_factor(self) -> Node:
        tok = self._curr_tok()
        leading_not = None
        if self._is_operator(tok, '!'):
            leading_not = self._parse_operator(tok.value())

        bool_factor = self._parse_bool_factor()

        if leading_not is None:
            return bool_factor
        leading_not.children = [bool_factor]
        return leading_not

    def _parse_bool_term(self) -> Node:
        factor1 = self._parse_not_bool_factor()

        while not self._no_more_tokens() and self._is_operator(self._curr_tok(), '&&'):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            factor2 = self._parse_not_bool_factor()
            op.children = [factor1, factor2]
            factor1 = op

        return factor1

    def _parse_bool_expression(self) -> Node:
        term1 = self._parse_bool_term()

        while not self._no_more_tokens() and self._is_operator(self._curr_tok(), '||'):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            term2 = self._parse_bool_term()
            op.children = [term1, term2]
            term1 = op

        return term1

    def _parse_print(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "print")

        print_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)

        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), '(')
        self._go_to_next_tok()
        str_node = self._parse_string_expression()
        self._match_operator(self._curr_tok(), ')')
        self._go_to_next_tok()
        self._match_operator(self._curr_tok(), ';')
        self._go_to_next_tok()

        print_node.children = [str_node]
        return print_node

    def _parse_optional_initialization(self, type_node: Node, ident_node: Node) -> Node:
        if not self._no_more_tokens() and self._is_operator(self._curr_tok(), '='):
            op_node = self._parse_operator('=')
            # tp = type_node.value()
            tp = ident_node.value().type
            if isinstance(tp, list):
                raise Parser.ArrayInitializationError(op_node.line, op_node.index)

            if tp in ("int", "double"):
                right_side_node = self._parse_arithmetic_expression()
            elif tp == "bool":
                right_side_node = self._parse_bool_expression()
            else:
                right_side_node = self._parse_string_expression()
            op_node.children = [ident_node, right_side_node]
            return op_node

        return ident_node

    def _parse_var_declaration(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, ("int", "double", "string", "bool"))
        type_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        decl_node = Parser.Node(self._parser_nodes_tbl, self._parser_nodes_tbl.index("declare"),
                                line=type_node.line, index=type_node.index)
        # decl_node.children.append(type_node)

        ident_node = self._parse_identifier_in_declaration(type_node)
        decl_node.children.append(self._parse_optional_initialization(type_node, ident_node))

        while not self._no_more_tokens() and self._is_operator(self._curr_tok(), ','):
            self._go_to_next_tok()  # skip ,
            ident_node = self._parse_identifier_in_declaration(type_node)
            decl_node.children.append(self._parse_optional_initialization(type_node, ident_node))

        self._match_operator(self._curr_tok(), ";")
        self._go_to_next_tok()

        return decl_node

    def _enter_current_block(self):
        self._current_level += 1

        if self._current_level >= len(self._blocks_on_levels):
            self._blocks_on_levels.append(0)

        self._blocks_on_levels[self._current_level] += 1
        block_num = self._blocks_on_levels[self._current_level]

        self._scope_stack.append((self._current_level, block_num))

    def _exit_current_block(self):
        self._current_level -= 1
        self._scope_stack.pop()

    def _parse_compound_statement(self) -> Node:
        tok = self._curr_tok()
        self._match_operator(tok, '{')

        self._enter_current_block()

        self._go_to_next_tok()
        statement = Parser.Node(self._parser_nodes_tbl, self._parser_nodes_tbl.index("compound_statement"),
                                line=tok.line, index=tok.index)

        while not self._no_more_tokens() and not self._is_operator(self._curr_tok(), '}'):
            statement.children.append(self._parse_statement())

        self._match_operator(self._curr_tok(), '}')
        self._exit_current_block()

        self._go_to_next_tok()
        return statement

    def _parse_assignment(self) -> Node:
        # ident_node = self._parse_identifier_in_using()
        ident_node = self._parse_identifier_in_using_or_indexation()

        op_node = self._parse_operator('=')
        # var_type = ident_node.value().type if indexation_node is None else ident_node.value().type[0]

        if self._is_identifier(ident_node):
            var_type = ident_node.value().type
        else:
            var_type = ident_node.children[0].value().type[0]

        if var_type in ("int", "double"):
            right_part = self._parse_arithmetic_expression()
        elif var_type == "bool":
            right_part = self._parse_bool_expression()
        else:
            right_part = self._parse_string_expression()

        # if indexation_node is not None:
        #     ident_node = indexation_node
        op_node.children = [ident_node, right_part]

        return op_node

    def _parse_if(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "if")
        if_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), "(")
        self._go_to_next_tok()

        condition_node = self._parse_bool_expression()
        self._match_operator(self._curr_tok(), ")")
        self._go_to_next_tok()

        statement_if = self._parse_statement()
        if_node.children = [condition_node, statement_if]

        if not self._no_more_tokens() and self._is_keyword(self._curr_tok(), "else"):
            self._go_to_next_tok()
            statement_else = self._parse_statement()
            if_node.children.append(statement_else)

        return if_node

    def _parse_while(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "while")
        while_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), "(")
        self._go_to_next_tok()

        condition_node = self._parse_bool_expression()
        self._match_operator(self._curr_tok(), ")")
        self._go_to_next_tok()

        self._num_loops += 1
        # self._inside_of_loop = True
        statement = self._parse_statement()
        # self._inside_of_loop = False
        self._num_loops -= 1

        while_node.children = [condition_node, statement]

        return while_node

    def _parse_for(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "for")
        for_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), "(")
        self._go_to_next_tok()

        # initialization
        init_node = None
        if not self._is_operator(self._curr_tok(), ";"):
            init_node = self._parse_assignment()
        self._match_operator(self._curr_tok(), ";")
        self._go_to_next_tok()

        condition_node = None
        if not self._is_operator(self._curr_tok(), ";"):
            condition_node = self._parse_bool_expression()
        self._match_operator(self._curr_tok(), ";")
        self._go_to_next_tok()

        iteration_node = None
        if not self._is_operator(self._curr_tok(), ")"):
            iteration_node = self._parse_assignment()
        self._match_operator(self._curr_tok(), ")")
        self._go_to_next_tok()

        # self._inside_of_loop = True
        self._num_loops += 1
        body_node = self._parse_statement()
        # self._inside_of_loop = False
        self._num_loops -= 1

        for_node.children = [init_node, condition_node, iteration_node, body_node]
        return for_node

    def _parse_switch(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "switch")
        switch_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), "(")
        self._go_to_next_tok()

        # expr_node, expr_type = self._parse_bool_arithm_or_string_expr()
        expr_node, expr_type = self._parse_switch_expression()
        self._switch_expression_types.append(expr_type)

        self._match_operator(self._curr_tok(), ")")
        self._go_to_next_tok()

        block_node = self._parse_compound_statement()

        # self._switch_expression_type = None
        self._switch_expression_types.pop()
        switch_node.children = [expr_node, block_node]
        return switch_node

    def _parse_break(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "break")
        break_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), ";")
        self._go_to_next_tok()
        return break_node

    def _parse_default(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "default")
        default_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), ":")
        self._go_to_next_tok()

        # statement_node = self._parse_statement()
        # default_node.children = [statement_node]

        return default_node

    def _parse_case(self) -> Node:
        tok = self._curr_tok()
        self._match_keyword(tok, "case")
        case_node = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()

        tok = self._curr_tok()
        switch_expr_type = self._switch_expression_types[len(self._switch_expression_types) - 1]
        # literal
        if switch_expr_type == "arithmetic":
            self._match_number(tok)
        elif switch_expr_type == "bool":
            self._match_bool_literal(tok)
        elif switch_expr_type == "string":
            self._match_string(tok)

        const = Parser.Node(tok.table, tok.index_in_table, None, tok.line, tok.index)
        self._go_to_next_tok()

        self._match_operator(self._curr_tok(), ":")
        self._go_to_next_tok()

        case_node.children = [const]
        return case_node

    def _parse_statement(self) -> Node:
        tok = self._curr_tok()

        self._check_for_forbidden_statements(tok)

        if self._is_keyword(tok, "print"):
            ret = self._parse_print()
        elif self._is_keyword(tok, "if"):
            ret = self._parse_if()
        elif self._is_keyword(tok, "while"):
            ret = self._parse_while()
        elif self._is_keyword(tok, "for"):
            ret = self._parse_for()
        elif self._is_keyword(tok, "switch"):
            ret = self._parse_switch()
        elif self._is_keyword(tok, "case"):
            ret = self._parse_case()
        elif self._is_keyword(tok, "break"):
            ret = self._parse_break()
        elif self._is_keyword(tok, "default"):
            ret = self._parse_default()
        elif self._is_operator(tok, "{"):
            ret = self._parse_compound_statement()
        elif self._is_identifier(tok):
            ret = self._parse_assignment()
            self._match_operator(self._curr_tok(), ';')
            self._go_to_next_tok()
        else:
            ret = self._parse_var_declaration()

        return ret

    def _parse_program(self) -> Node:
        prog = Parser.Node(self._parser_nodes_tbl, self._parser_nodes_tbl.index("program"))

        while not self._no_more_tokens():
            prog.children.append(self._parse_statement())

        return prog

    def create_syntax_tree(self):
        if len(self._tokens) == 0:
            return

        try:
            self._syntax_tree = self._parse_program()
        except Parser.ParserError as err:
            print(f"PARSER ERROR:\n{err}")
            sys.exit(1)

    def get_syntax_tree(self):
        return self._syntax_tree
