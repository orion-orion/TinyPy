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
            tokenizer = Tokenizer()
            tokens = tokenizer.tokenize(input_str)
            print(tokens)
        except (SyntaxError, NameError, TypeError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # Ctrl-C, Ctrl-D
            print()  # blank line
            break  # exit while loop (and end program)


if __name__ == "__main__":
    main()
