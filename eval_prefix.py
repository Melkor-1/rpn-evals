#!/usr/bin/env python3

import operator
from typing import Callable, Iterable, TypeVar, Union

OPCODES = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "^": operator.pow,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


def _eval_op(lhs: float, rhs: float, opcode: str) -> float:
    return OPCODES[opcode](lhs, rhs)


def _eval_expr(tokens: Iterable[Union[float, str]]) -> float:
    token_stack = []
    count_stack = []

    for token in tokens:
        if isinstance(token, (int, float)):
            # If the first token is an operand and there are more tokens
            # following it.
            if not token_stack and len(list(tokens)) > 1:
                raise ValueError("Invalid expression.")
            token_stack.append(token)

            if count_stack:
                count_stack[-1] -= 1
        else:
            if token in OPCODES:
                count_stack.append(2)  # Two operands left to be seen for the binary op.
            else:
                raise ValueError("Invalid operator seen.")
            token_stack.append(token)

        while count_stack and count_stack[-1] == 0:
            count_stack.pop()
            try:
                rhs = token_stack.pop()
                lhs = token_stack.pop()
                op = token_stack.pop()
                token_stack.append(_eval_op(lhs, rhs, op))
            except (ValueError, IndexError):
                raise ValueError("Invalid expression.")
            except ZeroDivisionError:
                raise ValueError("Can not divide by zero.")

            if count_stack:
                count_stack[-1] -= 1

    if len(token_stack) != 1 or count_stack:
        raise ValueError("Invalid expression.")

    if token_stack:
        return token_stack.pop()
    return 0


_T = TypeVar("T")
_U = TypeVar("U")


def _try_parse(value: _T, *parse_functions: Callable[[_T], _U]) -> _U:
    for parse_function in parse_functions:
        try:
            return parse_function(value)
        except ValueError:
            pass
    raise ValueError(f"Invalid symbol '{value}' found.")


def _tokenize_expr(expr: str) -> Iterable[Union[str, float]]:
    for token in expr.split():
        if token in OPCODES:
            yield token
        else:
            yield _try_parse(token, int, float)


def eval_prefix_expr(expr: str):
    """
    Evaluate a prefix expression.

    Supported operators:
        - Addition (+)
        - Subtraction (-)
        - Multiplication (*)
        - Division (/)
        - Floor Division (//)
        - Modulo (%)
        - Ordering - less than (<)
        - Ordering - less than or equal to (<=)
        - Ordering - greater than (>)
        - Ordering - greater than or equal to (>=)
        - Equality - equal to (==)
        - Difference - not equal to (!=)
    """
    tokens = _tokenize_expr(expr)
    return _eval_expr(tokens)


def main() -> None:
    test_data = [
        ("34", 34),
        ("+", None),
        (" + 1 2 3", None),
        ("+ 3 4", 7),
        ("+ -3 4", 1),
        ("+ ^ 5 4 + 3 4", 632),
        ("+ 10a 29", None),
        ("/ * 10 5 + 6 2", 6.25),
        ("- 10 + 7 * 2 3", -3),
        ("icaoscasjcs", None),
        ("1038 - // * 10 5 + 7 3 2", None),
        ("", 0),
        ("$ 9 2", None),
        ("+ 3e-08 2.1", 2.10000003),
        ("+ < 1 9 9", 10),
        ("== 1 1", 1),
    ]

    for expr, res in test_data:
        expr_repr = repr(expr)
        print(f"expr: {expr_repr}", end="")
        try:
            rv = eval_prefix_expr(expr)
            assert rv == res, f"Expected: {res}, Received: {rv}"
        except Exception as e:
            rv = e
        print(f", result: {repr(rv)}")


if __name__ == "__main__":
    main()
