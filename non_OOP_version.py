# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 21:08:32 2020

@author: Brian Glassman
"""

import operator

# The simple answer, if input is clean and trustworthy:
# eval(eqn)
# Never ever to be used in production code, but if it's a one-shot with known inputs...

#%% Operator Map
op_map = {'+': operator.add,
          '-': operator.sub,
          '*': operator.mul,
          'x': operator.mul, # Allow using x as a multiplication operator
          'X': operator.mul, # Allow using x as a multiplication operator
          '/': operator.truediv,
          }

#%% P - Parenthesis
def _match_paren(eqn, idx_open):
    """Returns the contents enclosed by the set of parenthesis opened at
    idx_open and the index of the closing parenthesis
    So if eqn=1+(2+3)+4, call would be match_paren(eqn, 2) which would return
    ('2+3', 6)
    """
    count = 1 # Initialize at 1, since this function only gets called after '('
    idx = idx_open + 1
    for c in eqn[idx_open+1:]:
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
            if count == 0:
                # All parenthesis matched
                return eqn[idx_open+1:idx], idx
        idx += 1
    # Finished searching without matching parenthesis
    raise ValueError(f"{count} too many open parenthesis")

def p_solver(eqn):
    """eqn should be a string with no whitespace"""

    while 1: # Python idiom for a do-while loop
        idx_open = eqn.find('(')
        if idx_open == -1:
            # No more parenthesis, break the loop
            return eqn
        else:
            # Parenthesis found, extract the contents
            inner, idx_close = _match_paren(eqn, idx_open)
            solved = str(pemdas_solver(inner))
            if debug: print('l', eqn[:idx_open])
            if debug: print('s', solved)
            if debug: print('r', eqn[idx_close+1:])
            eqn = eqn[:idx_open] + solved + eqn[idx_close+1:]

#%% num_op
def num_op(eqn):
    """Converts eqn (a string with no whitespace or parenthesis) into a list
    of numbers and operators
    # NOTE: Uses isdecimal instead of isdigit or isnumeric to avoid non-Arabic or non-decimal input
    """
    out = [] # Running output list
    num = [] # List that will be filled with numeric characters to convert
    for c in eqn:
        if c.isdecimal() or c == '.':
            # Start or continuation of a number, track it
            num.append(c)
        else:
            if num:
                # End of a number, convert and append
                out.append(float(''.join(num)))
                num.clear()

            if c in op_map:
                # Operator, convert and append
                out.append(op_map[c])
            else:
                # Unknown operator or bad input
                raise ValueError(f"Unknown operator or bad input: '{c}'")
    if num:
        # Last character should always be the end of a number
        out.append(float(''.join(num)))
    return out

# TODO check for doubled-up operators or numbers without operators

#%% E - Exponents
# TODO

#%% MD - Multiply/Divide
def md_solver(eqn):
    """Applies multiplication and division operations
    eqn should be an alternating list of numbers and operators"""

    # TODO remove this check if unary operators are added
    assert len(eqn) % 2 == 1, "eqn length is even, likely unbalanced operators"

    if len(eqn) <= 1:
        # Trivial case
        return eqn

    # TODO use a FIFO instead of list for eqn

    out = []
    left = eqn.pop(0)
    while 1: # Python idiom for do-while loop
        op = eqn.pop(0)
        right = eqn.pop(0)
        if op in (operator.mul, operator.truediv):
            # Correct precedence level, apply
            ans = op(left, right)

            # Check for finished iteration
            if len(eqn) == 0:
                # Done. Save the resulting value and exit
                out.append(ans)
                return out
            else:
                # Advance to next operator
                left = ans
        else:
            # Later precedence level, do not apply
            out.extend([left, op])

            if len(eqn) == 0:
                # Done. Save the leftover value and exit
                out.append(right)
                return out
            else:
                # Advance to next operator
                left = right

#%% AS - Add/Subtract
def as_solver(eqn):
    """Applies multiplication and division operations
    eqn should be an alternating list of numbers and operators"""

    # TODO remove this check if unary operators are added
    assert len(eqn) % 2 == 1, "eqn length is even, likely unbalanced operators"

    if len(eqn) <= 1:
        # Trivial case
        return eqn

    # TODO use a FIFO instead of list for eqn

    # NOTE: because addition/subtraction is the lowest precedence, can take
    # some shortcuts
    # TODO remove shortcuts and make more like mult_solver if unary operators are added

    out = []
    left = eqn.pop(0)
    while 1: # Python idiom for do-while loop
        op = eqn.pop(0)
        right = eqn.pop(0)

        # All operators are correct precedence level, apply
        ans = op(left, right)

        # Check for finished iteration
        if len(eqn) == 0:
            # Done. Save the resulting value and exit
            out.append(ans)
            return out
        else:
            # Advance to next operator
            left = ans

#%% PEMDAS - Wrapper
def pemdas_solver(eqn):
    try:
        eqn = p_solver(eqn)
        if debug: print(eqn)
        # eqn = e_solver(eqn)
        # if debug: print(eqn)
        eqn = num_op(eqn)
        if debug: print(eqn)
        eqn = md_solver(eqn)
        if debug: print(eqn)
        eqn = as_solver(eqn)
        if debug: print(eqn)
        assert len(eqn)==1, "Did not fully collapse equation"
        return eqn[0]
    except:
        print(eqn)
        raise

def total_solver(eqn):
    """Parses the mathematic equation in eqn
    eqn should be a text string with numbers, operators, and parenthesis"""
    eqn = ''.join(eqn.split()) # Remove whitespace
    if debug: print(eqn)
    return pemdas_solver(eqn)


#%% Test cases

debug = False

def test(text):
    print(text)
    ans = eval(text.replace('x','*').replace('X','*'))
    solved = total_solver(text)
    if solved == ans:
        print(f"Passed")
    else:
        print(f"FAILED. Should be {ans}, returned {solved}")

#TODO? Use an actual testing setup, just for fun

# Examples from assignment
text = '1 + 1' ; test(text)
text = '(3 + 4) * 6' ; test(text)
text = '(1 * 4) + (5 * 2)' ; test(text)

# PEMDAS test
text = '1 + 3 + 2 * 4' ; test(text)

# Complex test
text = '1+(2x3)+4*((5+6)+7 X 8 + (((9 * 10) * 11) x 12))' ; test(text)

# TODO Parenthetical multiplication
# text = '3(4)' ; test(text)
# text = '3+2(4+2)' ; test(text)
# text = '(3+2)(4+2)' ; test(text)

# Non-integers
text = '1.02 + 3.1' ; test(text)

# TODO? Scientific notation
# text = '1e3 + 2e2' ; test(text)

# Inconsistent spaces
text = '(1 *4) +(     5 * 2)' ; test(text)

# TODO? Dirty input
#   Bad math syntax
#   Unmatched parenthesis

#%% Tests that are NOT needed
# Symbolic variables
