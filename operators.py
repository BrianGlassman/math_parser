# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 09:38:00 2020

@author: Brian Glassman
"""


"""
Class definitions for the base MyOp and MyEnclosingOp class, specific operators, and wrapper functions
"""

from copy import deepcopy
import re
from abc import ABC
import operator # allows accessing functions for normal operators (ex. +, -, *, /)

class MyOp(ABC):
    """Abstract base class representing a generalized operator"""
    # What character(s) represent this operator in strings
    # A compiled regex
    token = None

    # Number of operands used (i.e. '+' has 1 left, 1 right)
    nleft = 0
    nright = 0

    # What function to apply to the operands
    func = None

    def __init__(self, left=None, right=None):
        """Generic init implementation, setting left and right operands"""
        # Operand contents
        self.left = left
        self.right = right

    def __repr__(self):
        """For readable output, use the class name followed by operands
        If operands are none, print blanks
        Add with no operands --> Add(,)
        Add with left=1, right=2 --> Add(1,2)"""
        name = self.__class__.__name__
        left = self.left
        right = self.right
        left = '' if left is None else left
        right = '' if right is None else right
        return f"{name}({left},{right})"

    def __eq__(self, other):
        """Generic equality check. Checks class type and operands"""
        return (isinstance(other, self.__class__)
                and other.left == self.left
                and other.right == self.right)

    def apply(self):
        """Apply the operator to the operands. If operands are MyOps, they are
        applied using postorder traversal"""
        # Apply each operand (if used)
        if self.nleft and isinstance(self.left, MyOp):
            self.left = deepcopy(self.left).apply()
        if self.nright and isinstance(self.right, MyOp):
            self.right = deepcopy(self.right).apply()

        # Apply the function
        args = []
        if self.nleft:
            args.append(self.left)
        if self.nright:
            args.append(self.right)
        return self.func(*args)

    @classmethod
    def tokenize(cls, eqn):
        """Replace instances of this operator in text with MyOp object
        eqn - a list of strings and/or MyOps
        returns a list of strings and/or MyOps, with text instances of this
        operator converted to MyOp objects"""
        if not isinstance(eqn, list):
            raise ValueError("Input to tokenize must be a list")

        out = [] # Running list of strings and MyOps so far
        for item in eqn:
            if isinstance(item, str):
                last_end = 0 # Where the last match ended
                # Iterate over matches to the token regex
                for match in re.finditer(cls.token, item):
                    start = match.start()
                    if start > last_end:
                        # Save substring before token, if there is any
                        out.append(item[last_end:start])
                    out.append(cls()) # Convert token to MyOp and append
                    last_end = match.end() # Update the pointer to avoid duplication
                if last_end < len(item):
                    out.append(item[last_end:]) # Save any leftovers
            elif isinstance(item, MyOp):
                # Already tokenized, skip
                out.append(item)
            else: raise ValueError("eqn contained something neither string nor MyOp")
        return out

    def consume(self, eqn, i):
        """Consumes MyOp's operands, modifying eqn inplace
        eqn - the equation to operate on, a list of MyOp objects
        i - index of this operator in eqn
        returns the index after consumption
        (to account for consumption of left operands)"""
        # Consume operands (start from right to preserve index)
        if self.nright:
            # Consume the right operand, don't change i
            try:
                self.right = eqn.pop(i+1)
            except IndexError:
                raise ValueError(f"Operator at end of eqn that needs right operand: {eqn}")
        if self.nleft:
            # Consume the left operand, reduce i by 1
            if i == 0: # list.pop(-1) won't error, so can't use try/except
                raise ValueError(f"Operator at start of eqn that needs left operand: {eqn}")
            self.left = eqn.pop(i-1)
            i -= 1
        return i

class MyEnclosingOp(MyOp):
    """Base class for a  two-part operator (open and close) that operates on
    the equation contained between the two.
    Children should be in pairs, an Open and Close (ex. OpenParen, CloseParen)
    The Open class does the processing, Close class is just a marker for parsing"""

    # Enclosed operands
    enclosed = None

    # Reference to the Closing operator class. None in closing operators themselves
    close = None

    def __init__(self, enclosed=None):
        """Generic enclosing init implementation, setting enclosed"""
        self.enclosed = enclosed

    def __repr__(self):
        """For readable output, use the class name followed by operands
        If operands are none, print blanks
        OpenParen with no enclosed operands --> OpenParen()
        OpenParen enclosing 1+2 --> OpenParen(1,Add(),2) or OpenParen(Add(1,2))"""
        name = self.__class__.__name__
        enclosed = self.enclosed
        enclosed = '' if enclosed is None else enclosed
        return f"{name}({enclosed})"

    def __eq__(self, other):
        """Generic equality check. Checks class type and contents"""
        return (isinstance(other, self.__class__)
                and other.enclosed == self.enclosed)

    def apply(self):
        """Apply the operator to the operands. If operands are MyOps, they are
        applied using postorder traversal"""
        # Apply each operand (if used)
        if self.enclosed and isinstance(self.enclosed, MyOp):
            self.enclosed = deepcopy(self.enclosed).apply()

        # Apply the function
        args = []
        if self.enclosed:
            args.append(self.enclosed)
        return self.func(*args)

    def consume(self, eqn, i):
        """Consumes all operands between this operator and the matching closing
        operator, modifying eqn inplace
        eqn - the equation to operate on, a list of MyOp objects
        i - index of this operator in eqn
        returns the resulting index after consumption
        (to account for consumption of left operands)"""
        if self.close is None:
            # self is a closing operator
            raise ValueError(f"Unmatched or out-of-order closing operator found {eqn}")

        # Iterate over eqn to find the matching Close operator, consuming
        # along the way
        self.enclosed = [] # Part of eqn enclosed by this operator
        count = 1 # Number of Open operators minus number of Close operators seen
        while count != 0:
            if i == len(eqn)-1:
                # Nothing after self, but still have unmatched Opens
                raise ValueError(f"{count} too many opening operators")
            op = eqn.pop(i+1) # Consume the next operator (right of self)
            if isinstance(op, self.__class__):
                # Open, increase count
                count += 1
            elif isinstance(op, self.close):
                # Close, decrease count
                count -= 1
                if count == 0:
                    # All Start/Stop operators matched
                    break # Exit the loop without appending the closeing operator
            self.enclosed.append(op) # Save the operator
        # Re-tokenize Neg to catch Sub instances adjacent to parentheses
        self.enclosed = Neg.tokenize(self.enclosed)
        # Convert contents to syntax tree
        self.enclosed = make_tree(self.enclosed)
        # All consumption is at or right of i, so no change needed
        return i

# Define close before open so that open can reference close
class CloseParen(MyEnclosingOp):
    token = re.compile('\)') # ")"
    close = None

class OpenParen(MyEnclosingOp):
    token = re.compile('\(') # "("
    close = CloseParen

    func = lambda self, enclosed: enclosed # Return operands unchanged

class Pow(MyOp):
    token = re.compile('\^|\*\*') # Allow "^" or "**"
    nleft = 1
    nright = 1
    func = operator.pow

class Mul(MyOp):
    token = re.compile('\*|x|X') # Allow "x" and "X" since no symbolic input allowed
    nleft = 1
    nright = 1
    func = operator.mul

class Div(MyOp):
    token = re.compile('/')
    nleft = 1
    nright = 1
    func = operator.truediv

class Add(MyOp):
    token = re.compile('\+') # "+"
    nleft = 1
    nright = 1
    func = operator.add

class Sub(MyOp):
    token = re.compile('-')
    nleft = 1
    nright = 1
    func = operator.sub

class Neg(MyOp):
    token = re.compile('-')
    nright = 1
    func = operator.neg

    @classmethod
    def tokenize(cls, eqn):
        """Overload of the tokenize method because Neg and Sub share a token
        Replaces Sub MyOps with Neg if the left operand uses a right operand
        Examples:
            Num(1), Sub(), Num(2) -->  Num(1), Sub(), Num(2)
                because Num(1).nright == 0
            Num(1), Mul(), Sub(), Num(2) --> Num(1), Mul(), Sub(), Num(2)
                because Mul().nright == 1 """
        assert isinstance(eqn, list)

        out = list(eqn) # Duplicate base class functionality of not modifying source list
        # Iterate over eqn, converting unary Subs to Neg
        for i, item in enumerate(eqn):
            if isinstance(item, Sub):
                # Sub MyOp found, check if it's actually a Neg
                if (i == 0 # No left operand possible, is Neg
                    or isinstance(eqn[i-1], MyOp) # Left operand is MyOp
                    and eqn[i-1].nright # Left operand uses a right operand
                    ):
                    out[i] = cls()
        return out

class Num(MyOp):
    """Special case of MyOp to allow numbers to be handled the same way as
    other MyOps"""
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        name = self.__class__.__name__
        value = self.value
        value = '' if value is None else value
        return f"{name}({value})"

    def __eq__(self, other):
        """Num equality check. Checks class type and value"""
        return (isinstance(other, self.__class__)
                and other.value == self.value)

    def apply(self):
        """Evaluates the number, returning the value"""
        return self.value

    @classmethod
    def tokenize(cls, eqn):
        """Overload of the tokenize method to convert all remaining strings to
        Nums (int or float, as appropriate)"""
        if not isinstance(eqn, list):
            raise ValueError("Input to tokenize must be a list")

        out = list(eqn) # Duplicate base class functionality of not modifying source list
        # Iterate over eqn, converting strings to Numbers
        for i, item in enumerate(eqn):
            if isinstance(item, str):
                # String operator found, convert to Number
                try:
                    temp = float(item)
                except ValueError:
                    raise ValueError(f"Unknown operator or bad input: '{item}'")
                if temp.is_integer():
                    out[i] = cls(int(temp))
                else:
                    out[i] = cls(temp)

        return out

# Convert operators in parse order (needed for unary "-" vs binary "-")
parse_order = [OpenParen,
               CloseParen,
               Pow,
               Mul,
               Div,
               Add,
               Sub,
               Neg, # Neg has to be after Sub and all other operators, since it replaces Subs with Negs
               Num, # Num has to be last, since it collects any remaining strings
               ]
# Apply operators in precedence order (levels must be tuples for isinstance checks)
prec_order = [(Num,),
              (OpenParen,CloseParen), # CloseParen just used for error-checking
              (Neg,),
              (Pow,),
              (Mul, Div),
              (Add, Sub),
              ]

def parse(text):
    """Parse text, converting operator tokens into MyOp instances
    Does no evaluation, and does not set operands
    text - string to be converted
    returns a list of MyOp objects"""
    assert isinstance(text, str)

    # Convert all operator tokens to MyOp instances, obeying parse order
    eqn = [text]
    for op in parse_order:
        eqn = op.tokenize(eqn)
    return eqn

def make_tree(eqn):
    """Convert eqn into a syntax tree
    eqn - a list of MyOp objects
    returns a single MyOp that is the root of the sytax tree"""
    out = deepcopy(eqn) # Copy to preserve input
    for level in prec_order:
        # Iterate over the list, consuming items as appropriate
        i = 0
        while i < len(out): # Use while instead of for because i changes mid-loop
            item = out[i]
            if isinstance(item, level):
                # MyOp found, incorporate the operands
                i = item.consume(out, i)
            # Advance i for the next item
            i += 1
    if len(out) != 1:
        raise ValueError("Tree did not fully collapse. Invalid input")
    return out[0]

def process(text):
    """Evaluate the string given in text. Equivalent to Python's eval function
    text - string representing an arithmetic expression to evaluate
    returns the value of text"""
    # Remove whitespace
    text = ''.join(text.split())
    # Convert string to list of MyOps
    parsed = parse(text)
    # Convert list to syntax tree
    treed = make_tree(parsed)
    # Evaluate the tree
    val = treed.apply()
    return val
