=========================================
TASK DESCRIPTION:
Task:
	Develop an arithmetic parser that takes in a string and evaluates it to return a value
	Support at least addition, multiplication, and parenthesis
	Deliverable should be a zip file with name in the title

Example Inputs:
	1 + 1
	(3 + 4) * 6
	(1 * 4) + (5 * 2)

Constraints and details:
	Write in an Object Oriented fashion
	Do not use the Shunting Yard Algorithm
	Symbolic inputs (ex. "a + 3 * 4") will not be used. Input will be either whitespace, operators, or numeric
	Input may not be clean. At least basic input validation is needed
	Purpose is to evaluate proficiency and problem solving so code quality, comments, and organization is more important than efficiency

Evaluation factors:
	readability
	extensibility
	overall organization
		
=========================================
USAGE:
run process(text) from parser.py, where "text" is the expression to be evaluated
	
=========================================
FUNCTIONALITY:
Take in a string containing an arithmetic expression with arbitrary whitespace, return the value represented by the expression
Supported operations and tokens (including multi-character tokens)
	Parentheses: (, )
	Exponent: **, ^
	Multiplication: *, x, X
	Division: /
		Note: Operator is applied only to the immediately adjacent operand, so "1/2+3" evaluates as "(1/2)+3" rather than "1/(2+3)"
	Addition: +
	Subtraction: -
	Negation: -
		Note: Subtraction and Negation use the same token
		Note: Repeated negations (ex. "--5") are not considered valid input
	
=========================================
DEVELOPMENT/IMPLEMENTATION NOTES:
As justification for using OOP, I treated the intent of the problem as developing a parser for arbitrary operators. Numeric values and arithmetic operators are treated as stand-ins for much more complicated hypothetical objects. This leads to more complexity than needed for this simple case, but easy extensibility.

Parsing is done by levels (ex. multiplication in the entire input, then addition) rather than left-to-right to avoid using the Shunting Yard Algorithm by accident. This makes the overall algorithm less efficient, scaling with the number of parsing levels.

Steps:
	Parse the string, converting everything to Operators (numeric values are converted to Number Operators for homogenous typing and easy processing)
	Convert the list of Operators into a syntax tree
	Evaluate the tree (postorder traversal)

In testing.py, imports are done inside the test classes/functions to minimize how many classes/functions are in scope.

Some comments are seemingly overkill. In my experience, comments that seemed unnecessary when writing allow for at-a-glance understanding when coming back to old code after 6 months.

In several places data is copied instead of modified inplace to preserve the original data. This is usually not necessary, but when optimization is unimportant it's better to err on the side of caution.
	In a production environment and/or when dealing with sufficiently long input strings, this would be the first place to look for optimization
	
Wrapper functions and operators are defined in the same file to avoid circular imports because processing parentheses requires calling the make_tree function.
		
=========================================
POSSIBLE FUTURE WORK:
Implement examples of arbitrary functions, since multi-character tokens that include numbers are possible
	ex. 'rad2deg' or 'do_something' would be valid operators
Parenthetical multiplication (i.e. "3(5+7)" is evaluated as "3*(5+7)")
	should be possible by allowing left operand to OpenParen and right operand to CloseParen, with OpenParen.apply and Neg.tokenize modified to account for it
Scientific notation
	Make "e" an operator equivalent to Pow(left, 10*right)
Rework operands to be more generic, to allow more versatile operators
	ex. an operator that has two right operands ("1 + op 2 3 + 4" --> "1 + op(2,3) + 4")
	Was initially considered (hence nleft and nright), but deemed out of scope with limited RoI
Make the parsing order and precedence order configurable, so that new operators can be easily defined at runtime
Develop a more general way of parsing Neg operators