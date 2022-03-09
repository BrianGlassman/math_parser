# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 18:50:42 2020

@author: Brian Glassman
"""

import unittest

# from operators import Num, Neg, OpenParen, CloseParen, Pow, Mul, Div, Add, Sub
# from operators import parse, make_tree, process

class TestTokenizer(unittest.TestCase):
    """Test the tokenize method of MyOp class directly
    Tokenize assumes that input is already a list of strings and/or MyOps"""
    def test_all_tokens(self):
        """Test trivial cases, just the operator"""
        from operators import Neg, OpenParen, CloseParen, Pow, Mul, Div, Add, Sub
        examples = [# Groups are [input, class]. Expected output is class()
                    ('(', OpenParen),
                    (')', CloseParen),
                    ('**', Pow),
                    ('^', Pow),
                    ('*', Mul),
                    ('X', Mul),
                    ('x', Mul),
                    ('/', Div),
                    ('+', Add),
                    ('-', Sub),
                    (Sub(), Neg), # Neg.tokenize expects to receive input after Sub.tokenize has been applied
                    ]
        for ex_in, cl in examples:
            self.assertEqual([cl()], cl.tokenize([ex_in]), f"{ex_in} {cl.__name__}")
    def test_generic_tokenizer(self):
        """Test simple cases
        Use Mul as an arbitrary example"""
        from operators import Mul, Pow, Num, Add
        examples= [ # Input and output are grouped together
                   # Valid input
                   (['2*3'], # Trivial case
                    ['2',Mul(),'3']),
                   (['1+2*3'], # Mixed input. Tokenize *, ignore +
                    ['1+2',Mul(),'3']),
                   (['1+2'], # No tokenizing needed, make no change
                    ['1+2']),
                   ([Num(1), Add(), Num(2)], # Already tokenized, make no change. 1 + 2
                    [Num(1), Add(), Num(2)]),
                   ([Pow(Num(2),Num(3)), '*5'], # Partially tokenized. 2**3 * 5
                    [Pow(Num(2),Num(3)), Mul(), '5']),
                   # Invalid expressions, but can be tokenized
                   (['1+2*'], # Token at end
                    ['1+2',Mul()]),
                   (['*1+2'], # Token at start
                    [Mul(),'1+2']),
                   ]
        for ex_in, ex_out in examples:
            self.assertEqual(ex_out, Mul.tokenize(ex_in), ex_in)
    def test_num_tokenizer(self):
        """Test tokenizing numbers"""
        from operators import Num
        examples = [# Input and output are grouped together
                    ('5', Num(5)),
                    ('12345', Num(12345)),
                    ('123.456', Num(123.456)),
                    ('0.0001', Num(0.0001)),
                     ]
        for ex_in, ex_out in examples:
            actual_out = Num.tokenize([ex_in])
            self.assertEqual([ex_out], actual_out, ex_in)
    def test_special_tokenizer(self):
        """Test special token functionality"""
        from operators import Pow, Mul
        examples= [ # Groups are: [input, expected output, function to use]
                   (['2**3'], # Multi-character operator
                    ['2', Pow(), '3'],
                    Pow.tokenize),
                   (['2*3'], # Operator with multiple tokens
                    ['2', Mul(), '3'],
                    Mul.tokenize),
                   (['2x3'], # Operator with multiple tokens
                    ['2', Mul(), '3'],
                    Mul.tokenize),
                   (['2X3'], # Operator with multiple tokens
                    ['2', Mul(), '3'],
                    Mul.tokenize),
                   ]
        for ex_in, ex_out, func in examples:
            self.assertEqual(ex_out, func(ex_in),
                             f"{ex_in} --> {func(ex_in)}    Should be {ex_out}")

class TestParse(unittest.TestCase):
    """Test the parse top-level function
    parse assumes that input is a string with no whitespace"""

    def test_parse_noParen(self):
        """Test without parentheses"""
        from operators import Num, Neg, Mul, Div, Add, Sub
        from operators import parse
        ex_in = '1+2*3.5-4/5+-6'
        ex_out = [Num(1), Add(), Num(2), Mul(), Num(3.5), Sub(), Num(4), Div(), Num(5), Add(), Neg(), Num(6)]
        self.assertEqual(ex_out, parse(ex_in))

    def test_parse_withParen(self):
        """Test with parentheses"""
        from operators import Num, Neg, OpenParen, CloseParen, Mul, Div, Add, Sub
        from operators import parse
        ex_in = '(1+2)*(3.5-4)/5+-6'
        ex_out = [OpenParen(), Num(1), Add(), Num(2), CloseParen(), Mul(),
                  OpenParen(), Num(3.5), Sub(), Num(4), CloseParen(), Div(),
                  Num(5), Add(), Neg(), Num(6)]
        self.assertEqual(ex_out, parse(ex_in))

class TestTree(unittest.TestCase):
    def test_tree_noParen(self):
        from operators import Num, Neg, Mul, Div, Add, Sub
        from operators import make_tree
        ex_in = [Num(1), Add(), Num(2), Mul(), Num(3.5), Sub(), Num(4), Div(), Num(2), Add(), Neg(), Num(5)]
        ex_out = Add(
                	 Sub(
                		 Add(
                			 Num(1),
                			 Mul(
                				 Num(2),
                				 Num(3.5)
                				 )
                			 ),
                		 Div(
                			 Num(4),
                			 Num(2)
                			 )
                		 ),
                	 Neg(None,Num(5))
                	 )
        self.assertEqual(ex_out, make_tree(ex_in))

    def test_tree_withParen(self):
        from operators import Num, Neg, OpenParen, CloseParen, Mul, Div, Add, Sub
        from operators import make_tree
        ex_in = [OpenParen(), Num(1), Add(), Num(2), CloseParen(), Mul(),
                  OpenParen(), Num(3.5), Sub(), Num(4), CloseParen(), Div(),
                  Num(5), Add(), Neg(), Num(6)]
        ex_out = Add(
                     Div(
                         Mul(
                             OpenParen(
                                       Add(
                                           Num(1),
                                           Num(2)
                                           )
                                       ),
                             OpenParen(
                                       Sub(
                                           Num(3.5),
                                           Num(4)
                                           )
                                       )
                             ),
                         Num(5)
                         ),
                     Neg(None, Num(6))
                     )
        self.assertEqual(ex_out, make_tree(ex_in))

class TestApply(unittest.TestCase):
    """Test the apply function, starting from a valid tree"""
    def test_apply_num(self):
        """Test that Num applies to return an int or float correctly"""
        from operators import Num
        examples = [# Input and output are grouped together
                    (Num(5), 5),
                    (Num(12345), 12345),
                    (Num(123.456), 123.456),
                    (Num(0.0001), 0.0001),
                     ]
        for ex_in, ex_out in examples:
            actual_out = ex_in.apply()
            self.assertEqual(ex_out, actual_out, ex_in)
            self.assertEqual(type(ex_out), type(actual_out), ex_in)

    def test_apply_noParen(self):
        from operators import Num, Neg, Mul, Div, Add, Sub

        ex_in = Add(Num(1), Num(5))
        ex_out = 1+5
        self.assertEqual(ex_out, ex_in.apply(), 'Simple Apply')

        ex_in = Add(Num(1),Mul(Neg(None,Num(2)),Num(3.2)))
        ex_out = 1+-2*3.2
        self.assertEqual(ex_out, ex_in.apply(), 'Negative Apply')

        ex_in = Add(Num(1),Mul(Num(2),Num(3.2)))
        ex_out = 1+2*3.2
        self.assertEqual(ex_out, ex_in.apply(), 'Intermediate Apply')

        ex_in = Add(Sub(Add(Num(1),Mul(Num(2),Num(3.4))),Div(Num(5),Num(6))),Neg(None,Num(7)))
        ex_out = 1+2*3.4-5/6+-7
        self.assertEqual(ex_out, ex_in.apply(), 'Complex Apply')

    def test_apply_withParen(self):
        from operators import Num, Neg, OpenParen, Mul, Div, Add, Sub

        ex_in = Add(Num(1), OpenParen(Num(5)))
        ex_out = 1+(5)
        self.assertEqual(ex_out, ex_in.apply(), 'Simple Apply')

        ex_in = Mul(OpenParen(Add(Num(1),Neg(None,Num(2)))),Num(3.2))
        ex_out = (1+-2)*3.2
        self.assertEqual(ex_out, ex_in.apply(), 'Negative Apply')

        ex_in = Add(Num(1),Mul(Num(2),Num(3.2)))
        ex_out = 1+2*3.2
        self.assertEqual(ex_out, ex_in.apply(), 'Intermediate Apply')

        ex_in = Add(Sub(Add(Num(1),Mul(Num(2),Num(3.4))),Div(Num(5),Num(6))),Neg(None,Num(7)))
        ex_out = 1+2*3.4-5/6+-7
        self.assertEqual(ex_out, ex_in.apply(), 'Complex Apply')


class TestFull(unittest.TestCase):
    """Test the full functionality, from string to value. Equivalent to eval"""
    def test_whitespace(self):
        """Python eval doesn't accept tabs and newlines, handle specially"""
        from operators import process
        for text in ['1+1', # No spaces
                     '  1 + 2', # Leading
                     '1 + 2 ', # Trailing
                     '(1 *4) +(     5 * 2)', # Inconsistent spacing
                     '1+2\n-3+4', # Newline
                     '1+2\t-3+4', # Tab
                     ]:
            python_answer = eval(text.replace('\t','').replace('\n',''))
            my_answer = process(text)
            self.assertEqual(my_answer, python_answer, text)
    def test_given(self):
        """Example input given in the assignment"""
        from operators import process
        for text in ['1 + 1',
                     '(3 + 4) * 6',
                     '(1 * 4) + (5 * 2)']:
            self.assertEqual(process(text), eval(text))
    def test_PEMDAS(self):
        """Test operator precedence"""
        from operators import process
        for text in ['1+3*5', # Mul before addition
                     '1*3+5', # Can't hurt to (quicklky) test extra
                     '(1+3)*5', # Parenthesis before multiplication
                     '1-2+3-4+5', # Add/Sub left to right
                     '1/2*3/4*5', # Mul/Div left to right
                     '1 + 3 + 2 * 4',
                      '-(1+3)', # Weird PEMDAS with unary -
                     ]:
            self.assertEqual(process(text), eval(text), text)
    def test_NegPrecedence(self):
        """Thorough precedence testing of Neg (unary -)"""
        from operators import process
        for text in ['-5', # Trivial case, negate a number
                     '-(1+3)', # Negate the output of a parenthetical
                     '1+(-5+2)', # Negate a number inside a parenthesis
                     '3*-2', # Negation with multiplication
                     '3+-2', # Negation with addition
                     '3--2', # Negation with subtraction, equivalent to 3 - (0-2)
                     ]:
            self.assertEqual(process(text), eval(text), text)
    def test_uncategorized(self):
        """Tests that don't fit any other pattern"""
        from operators import process
        for text in [
                     '(5)-3', # Edge case parentheses, tested in full just to be safe
                     '1.02 + 3.1', # Non-integers, tested in full just to be safe
                     '(1+2) * (3.5 - 4)/5 + -6',
                     '-1 + 2**2 * 3 + (4/2) + (-5)',
                     '1+(2*3) + 4 * ( ( 5 * 6) + 7*8 + (((9*10)*11)*12))',
                     '1 + (2 + (((3) + 4) + 5 ))',
                     ]:
            self.assertEqual(process(text), eval(text), text)
    def test_x_mult(self):
        from operators import process
        """Python eval doesn't allow "x" and "X" as multiplication, handle specially"""
        for text in ['2x3',
                     '2X3',
                     '1+(2x3)+4*((5+6)+7 X 8 + (((9 * 10) * 11) x 12))',
                     ]:
            python_answer = eval(text.replace('x','*').replace('X','*'))
            my_answer = process(text)
            self.assertEqual(my_answer, python_answer, text)

class TestBadInput(unittest.TestCase):
    """Test different kinds of bad input"""
    def test_unmatched_enclosing(self):
        """Unmatched parentheses"""
        from operators import process
        for text in ['(', # One unmatched open
                     '((((', # Many unmatched open
                     '1+(3*', # Unmatched open mid-expression, with invalid end operator
                     '1+(3*3', # Unmatched open mid-expression, with valid end operator
                     ]:
            count = text.count('(') - text.count(')')
            with self.assertRaisesRegex(ValueError, f"{count} too many opening operators", msg=text):
                process(text)
        for text in [
                     ')', # Unmatched close
                     '1+2)', # Unmatched close at end
                     '1+2)+3', # Unmatched close mid-expression
                     ')1+2(+3', # Right number of open/close, but wrong order
                     ]:
            count = text.count('(') - text.count(')')
            with self.assertRaisesRegex(ValueError, "Unmatched or out-of-order closing operator found", msg=text):
                process(text)
    def test_invalid_syntax(self):
        """Input that produces a SyntaxError using eval"""
        from operators import process
        self.assertRaisesRegex(ValueError, "Tree did not fully collapse. Invalid input",
                               process, '1+*4')
        self.assertRaisesRegex(ValueError, "Operator at end of eqn that needs right operand",
                               process, '3*')
        self.assertRaisesRegex(ValueError, "Operator at start of eqn that needs left operand",
                               process, '*3')
    def test_unknown_operator(self):
        """Input that Python can evaluate, but uses an operator that hasn't been implemented"""
        from operators import process
        for text in ['4%3', # Modulus not implemented
                     '1=5 + 2', # Equation, not expression
                     'foobar', # Not a math expression, but will be treated as unknown operator
                     ]:
            self.assertRaisesRegex(ValueError, "Unknown operator or bad input:",
                                   process, text)

if __name__ == '__main__':
    unittest.main()
