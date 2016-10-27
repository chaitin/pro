grammar pro;

program
	:	Identifier '{' statement* '}'
	;

statement
	:	call_statement
	|	declaration
	|	delimiter
	;

delimiter
	:	';'
	|	'\n'
	;

declaration
	:	type_specifier Identifier initializer?
	;

type_specifier
	:	'var'
	|	'const'
	|	'array'
	|	'func'
	;

initializer
	:	expression_initializer
	|	array_initializer
	|	func_initializer
	;

expression_initializer
	:	'(' expression ')'
	;

array_initializer
	:	'[' expression ']'
	;

func_initializer
	:	'<' Identifier (',' Constant (',' String)?)? '>'
	;

call_statement
	:	Identifier '(' arguments? ')'
	;

arguments
	:	expression
	|	arguments ',' expression
	;

expression
	:	primary_expression
	|	binary_expression
	|	unary_expression
	;

binary_expression
	:	primary_expression binary_operator primary_expression
	;

unary_expression
	:	unary_operator primary_expression
	;

binary_operator
	:	'+'
	|	'-'
	|	'*'
	|	'/'
	|	'^'
	|	'|'
	|	'&'
	;

unary_operator
	:	'&'
	;

primary_expression
	:	Identifier
	|	Constant
	|	String
	|	'(' expression ')'
	;

Identifier
	:	Nondigit (Nondigit | Digit)*
	;

Constant
	:	Decimal
	|	Hexadecimal
	;

Decimal
	:	'-'? Digit+
	;

Hexadecimal
	:	'-'? '0' ('x' | 'X') Hexdigit+
	;

String
	:	'"'	Char_sequence? '"'
	;

fragment
Char_sequence
	:	Char+
	;

fragment
Char
	:	~["\\]
	|	Escape_sequence
	;

fragment
Nondigit
	:	[a-zA-Z_]
	;

fragment
Digit
	:	[0-9]
	;

fragment
Hexdigit
	:	[0-9a-fA-F]
	;

fragment
Escape_sequence
	:	'\\' ["n\\]
	|	'\\x' Hexdigit+
	;

Whitespace
    :   [ \t]+
        -> skip
	;

LineComment
    :   ('//' | '#')  ~[\r\n]*
        -> skip
	;

BlockComment
    :   '/*' .*? '*/'
        -> skip
	;
