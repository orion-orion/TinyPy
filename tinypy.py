try:
    import readline  # history and arrow keys for CLI
except ImportError:
    pass  # but not everyone has it
import sys
from expr import global_env
from pyparser import Parser
from pytokenizer import Tokenizer


def main():
    """Run a read-eval-print loop(REPL).
    `python tinypy.py` to start an interactive REPL.
    `python tinpy.py --ast` to interactively read expressions and
      print their abstract syntax tree.
    """
    print_ast = len(sys.argv) == 2 and sys.argv[1] == '--ast'

    while True:
        try:
            input_str = input('>>> ')
            """Parse an expression from a string. If the string does not
            contain anexpression, None is returned. If the string cannot be
            parsed, a SyntaxError is raised.

            >>> from pyparser import Parser
            >>> from pytokenizer import Tokenizer
            >>> tokenizer = Tokenizer()
            >>> parser = Parser()
            >>> parser.parse(tokenizer.tokenize('lambda x: add(x, 2)'))
            Lambda(['x'], Application(Variable('add'),
            [Variable('x'), Literal(2)]))
            >>> parser.parse(tokenizer.tokenize('(lambda x: add(x, 2))(2)'))
            Application(Lambda(['x'], Application(Variable('add'),
            [Variable('x'), Literal(2)])), [Literal(3)])
            >>> parser.parse(tokenizer.tokenize('(lambda: 2)()'))
            Application(Lambda([], Literal(2)), [])
            >>> parser.parse(tokenizer.tokenize('lambda x y: 5'))
            SyntaxError: expected 'COLON' but got 'NAME'
            >>> tokenizer.tokenize('  '))
            []
            """
            tokenizer = Tokenizer()
            tokens = tokenizer.tokenize(input_str)
            parser = Parser()
            if tokens:
                ast = parser.parse(tokens)
            else:
                ast = None
            if ast is not None:
                if print_ast:
                    print(repr(ast))
                else:
                    print(ast.eval(global_env))
        except (SyntaxError, NameError, TypeError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # Ctrl-C, Ctrl-D
            print()  # blank line
            break  # exit while loop (and end program)


if __name__ == "__main__":
    main()
