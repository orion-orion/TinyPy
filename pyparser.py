from expr import Literal, Variable, Lambda, Application
from pytokenizer import Token


class Parser:

    def parse(self, tokens):
        self.tokens = iter(tokens)
        self.tok = None  # Last symbol consumed
        self.nexttok = None  # Next symbol tokenized
        self._advance()  # Load first lookahead token
        return self.expr()

    def _advance(self):
        """Cosume the next token and advance one token ahead."""
        self.tok, self.nexttok = self.nexttok, next(
            self.tokens, Token("None", None))

    def _accept(self, toktype):
        """Test and consume the next token if it matches the toktype."""
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        """Consume next token if it maches toktype, or raise SyntaxError."""
        if not self._accept(toktype):
            raise SyntaxError("expected '{}' but got '{}'".format(
                toktype, self.nexttok.type))

    def expr(self):
        """Begin to parse a expression."""
        if self.nexttok.type is None:
            raise SyntaxError('Incomplete expression')
        elif self._accept("LITERAL"):
            return self.application(Literal(self.tok.value))
        elif self._accept("NAME"):
            return self.application(Variable(self.tok.value))
        elif self._accept('LAMBDA'):
            # Parse all the parameters of lambda expression,
            params = self.comma_separated_list(self.param)
            self._expect("COLON")
            body = self.expr()
            return Lambda(params, body)
        elif self._accept("LPAREN"):
            # Parse the expression in the "()"
            inner_expr = self.expr()
            self._expect("RPAREN")
            return self.application(inner_expr)
        else:
            raise SyntaxError(
                "'{}' is not the start of an expression".format(
                    self.nexttok.type))

    def comma_separated_list(self, item_parser):
        """Parse a comma-separated list using the specified item parser.

        Args:
            item_parser (function): a function used to parse items in the
            comma-separated list.

        Returns:
            list: a list containing the parsed items.
        """
        # The nexttok is ":" or ) implies the lambda/built-in operator
        # expression has no parameter/arguments
        if self.nexttok.type in ["COLON", "RPAREN"]:  # ":" or ")"
            return []
        else:
            # Get the first parameter, it may be variable.
            # For built-in operator, it also may be expression
            items = [item_parser()]
            # The nexttok is ":" or ) implies the lambda/built-in operator
            # expression has more parameters/arguments
            while self.nexttok and self.nexttok.type == "COMMA":  # ","
                # Consume the ","
                self._advance()
                # And go on
                items.append(item_parser())
            return items

    def application(self, operator):
        """A precedure application containing operator and operands.
        Note that the operator and operands have not yet been evaluated, since
        a specific environment is required.

        Args:
            operator (Lambda or Variable): the operator can be lambda
            expression or built-in operator.

        Returns:
            Application: a procedure application.
        """
        # If the nexttok is "(", we begin to parse the operands of the operator
        while self.nexttok and self.nexttok.type == "LPAREN":
            # Consume the "("
            self._advance()
            # Get the list of operands
            operands = self.comma_separated_list(self.expr)
            self._expect("RPAREN")
            operator = Application(operator, operands)
        return operator

    def param(self):
        """Parse a parameter of a lambda expression."""
        self._advance()
        if self.tok.type == "NAME":
            return self.tok.value
        else:
            raise SyntaxError(
                "Expected parameter name but got '{}'".format(self.tok))
