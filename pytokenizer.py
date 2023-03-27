import string
import collections


Token = collections.namedtuple("Token", ["type", "value"])


class Tokenizer:

    SYMBOL_STARTS = set(string.ascii_lowercase + string.ascii_uppercase + '_')
    SYMBOL_INNERS = SYMBOL_STARTS | set(string.digits)
    NUMERAL = set(string.digits + '-.')
    WHITESPACE = set(' \t\n\r')
    DELIMITERS = set('(),:')

    def tokenize(self, s: str):
        """Splits the string s into tokens and returns a list of them.

        >>> tokenize('lambda x: add(x, 2)')
        [Token(type='LAMBDA', value='lambda'), Token(type='NAME', value='x'),
        Token(type='COLON', value=':'), Token(type='NAME', value='add'),
        Token(type='LPAREN', value='('), Token(type='NAME', value='x'),
        Token(type='COMMA', value=','), Token(type='LITERAL', value=2),
        Token(type='RPAREN', value=')')]
        """
        self.chs = iter(s)
        self.ch = None  # Last charater consumed
        self.nextch = None  # Next character to be visited
        self._advance()  # Load first lookahead character

        tokens = []
        while True:
            token = self.next_token()
            if token is None:
                return tokens
            if isinstance(token, int) or isinstance(token, float):
                tokens.append(Token("LITERAL", token))
            elif isinstance(token, str) and token not in self.DELIMITERS \
                    and token != 'lambda':
                tokens.append(Token("NAME", token))
            elif token == "lambda":
                tokens.append(Token("LAMBDA", token))
            elif token == ":":
                tokens.append(Token("COLON", token))
            elif token == ",":
                tokens.append(Token("COMMA", token))
            elif token == "(":
                tokens.append(Token("LPAREN", token))
            elif token == ")":
                tokens.append(Token("RPAREN", token))

    def _advance(self):
        """Consume the next character and advance one char ahead."""
        self.ch, self.nextch = self.nextch, next(
            self.chs, None)

    def consume(self, allowed_characters):
        """As long as the next character is allowed characters,
        we will consume and record it."""
        result = ''
        while self.nextch in allowed_characters:
            self._advance()
            result += self.ch
        return result

    def next_token(self):
        """Consume and return the next token."""
        self.consume(self.WHITESPACE)  # Consume all the whitespace
        # Now the next character is not a whitespace
        c = self.nextch
        if c is None:
            return None
        elif c in self.NUMERAL:
            # If the next character is a numeral, we will go on.
            literal = self.consume(self.NUMERAL)
            try:
                return int(literal)
            except ValueError:
                try:
                    return float(literal)
                except ValueError:
                    raise SyntaxError("'{}' is not a numeral".format(literal))
        elif c in self.SYMBOL_STARTS:
            # If the next character is a built-in symbol, we will go on.
            return self.consume(self.SYMBOL_INNERS)
        elif c in self.DELIMITERS:
            self._advance()
            return c
        else:
            raise SyntaxError("'{}' is not a token".format(c))
