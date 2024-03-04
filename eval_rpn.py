#!/usr/bin/env python3

import operator
from typing import (Callable, Iterable, TypeVar,  # For older Python versions.
                    Union)

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

OPCODES_DOCSTRING = """
Supported operators:
    - Addition (+)
    - Subtraction (-)
    - Multiplication (*)
    - Division (/)
    - Floor Division (//)
    - Modulo (%)
    - Exponentiation (^)
    - Ordering - less than (<)
    - Ordering - less than or equal to (<=)
    - Ordering - greater than (>)
    - Ordering - greater than or equal to (>=)
    - Equality - equal to (==)
    - Difference - not equal to (!=)
"""


def _eval_op(lhs: float, rhs: float, opcode: str) -> float:
    return OPCODES[opcode](lhs, rhs)


def _postfix_swap(a: float, b: float) -> float:
    return b, a


def _prefix_swap(a: float, b: float) -> float:
    return a, b


def _eval_expr(tokens: list[Union[float, str]], swap_func) -> float:
    operands = []

    for tok in tokens:
        if tok in OPCODES:
            try:
                lhs, rhs = swap_func(operands.pop(), operands.pop())
                operands.append(_eval_op(lhs, rhs, tok))
            except IndexError:
                raise IndexError("Invalid expression.")
            except KeyError:
                raise KeyError("Invalid operator.")
            except ZeroDivisionError:
                raise ZeroDivisionError("Can not divide by zero.")
        else:
            operands.append(tok)

    if len(operands) != 1:
        raise ValueError("Invalid expression.")
    return operands.pop()


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


def eval_postfix_expr(expr: str) -> float:
    """
    Evaluate a postfix expression.

    Supported operators:
        + - * / // % ^

        See OPCODES_DOCSTRING for more information.
    """
    tokens = _tokenize_expr(expr)
    return _eval_expr(tokens, _postfix_swap)


def eval_prefix_expr(expr: str) -> float:
    """
    Evaluate a prefix expression.

    Supported operators:
        + - * / // % ^

        See OPCODES_DOCSTRING for more information.
    """
    tokens = list(reversed(_tokenize_expr(expr)))
    return _eval_expr(tokens, _prefix_swap)


def main() -> None:
    test_data = [
        ("+", None),
        ("102 0 /", None),
        ("1 2 3 +", None),
        ("3 1 $", None),
        ("3 4 +", 7),
        ("2 *", None),
        ("3 4 + 5 4 ^ +", 632),
        ("+ 10a 29", None),
        ("10 5 * 6 2 + /", 6.25),
        ("10 7 2 3 * + -", -3),
        ("icaoscasjcs", None),
        ("* 10 5 * 7 3 + // 2 -", 3),
    ]

    for expr, res in test_data:
        expr_repr = repr(expr)
        print(f"expr: {expr_repr}", end="")
        try:
            rv = _eval_expr(_tokenize_expr(expr), _postfix_swap)
            assert rv == res, f"Expected: {res}, Received: {rv}"
        except Exception as e:
            rv = e
        print(f", result: {repr(rv)}")


if __name__ == "__main__":
    main()
