import operator

from utils import concat_comma_separated


class Expr:
    """When you type input into this interpreter, it is parsed into an
    "abstract syntax tree"(AST), which is actually a recursively defined
    expression.

    In our interpreter, there are four types of expressions:
        - literals, which are simply numbers (e.g. 42 or 4.2)
        - variables (e.g. my_awesome_variable_name)
        - procedure applications (e.g. add(2, 3))
        - lambda expressions (e.g. lambda x: add(x + 2))

    Recursive definitions means precedure applications and lambda expressions
    are built from subexpressions. A lambda's body and a procedure
    application's operator and operands can also be expressions as well.

    In our code, the four types of expressions are subclasses of the `Expr`
    class: `Literal`, `Variable`, `Application`, and `Lambda`.
    """

    def __init__(self, *args):
        self.args = args

    def eval(self, env):
        """Each subclass of Expr will override the eval method.`env` is a
        dictionary mapping strings to `Value` instances, representing the
        environment in which this expression is being evaluated. This method
        should return a `Value` instance, the result of evaluating the
        expression.
        """

    def __str__(self):
        """Returns a parsable and human-readable string of this expression
        (i.e. what you would type into the interpreter).

        >>> expr = Application(Lambda(['x'], Variable('x')), [Literal(5)])
        >>> str(expr)
        '(lambda x: x)(5)'
        """
        raise NotImplementedError

    def __repr__(self):
        """Returns how the expression is written in a abstract syntax tree..

        >>> expr1 = Lambda(['x'], Application(Variable('add'), [Variable('x'),\
        Literal(2)]))
        >>> expr1
        Lambda(['x'], Application(Variable('add'), [Variable('x'),\
        Literal(2)]))

        >>> expr2 = Application(Lambda([], Literal(2)), [])
        >>> expr2
        Application(Lambda([], Literal(2)), [])
        """
        args = '(' + concat_comma_separated([repr(arg)
                                             for arg in self.args]) + ')'
        return type(self).__name__ + args


class Literal(Expr):
    """A literal is notation for representing a fixed value in code. In our
    tiny python , the only literals are numbers, which means `Literal` should
    always be self-evaluated(i.e. be evaluated without environment) to a
    `Number` value.

    The `value` attribute contains the fixed value the `Literal` refers to,
    such as int or float in python.
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def eval(self, env):
        """the literal is evaluated without environment. """
        return Number(self.value)

    def __str__(self):
        return str(self.value)


class Variable(Expr):
    """A `Variable` is a variable. When evaluated, we look up the value of the
    variable in the current environment.

    The `var_name` attribute contains the name of the variable (as a Python
    string).
    """

    def __init__(self, var_name):
        super().__init__(var_name)
        self.var_name = var_name

    def eval(self, env):
        """
        >>> env = {
        ...     'a': Number(1),
        ...     'b': LambdaProcedure([], Literal(2), {})
        ... }
        >>> Variable('a').eval(env)
        Number(1)
        >>> Variable('b').eval(env)
        LambdaProcedure([], Literal(2), {})
        >>> print(Variable('c').eval(env))
        None
        """
        if self.var_name in env.keys():
            return env[self.var_name]
        else:
            return None

    def __str__(self):
        return self.var_name


class Lambda(Expr):
    """A lambda expression, which evaluates to a `LambdaProcedure`.

    The `parameters` attribute is a list of variable names (a list of strings).
    The `body` attribute is an instance of `Expr`.

    For example, the lambda expression `lambda x: add(x, 2)` is parsed as

    Lambda(['x'], Application(Variable('add'), [Variable('x'), Literal(2)]))

    where `parameters` is the list ['x'] and `body` is the expression
    Application(Variable('add'), [Variable('x'), Literal(2)]))
    """

    def __init__(self, parameters, body):
        super().__init__(parameters, body)
        self.parameters = parameters
        self.body = body

    def eval(self, env):
        """ A lambda procedure is a lambda expression that knows the
        environment in which it was evaluated in.
        >>> Lambda(['x'], Application(Variable('add'), [Variable('x'),\
        Literal(2)])).eval(global_env)
        <function lambda x: add(x, 2)>
        """
        return LambdaProcedure(self.parameters, self.body, env)

    def __str__(self):
        body = str(self.body)
        if not self.parameters:
            return 'lambda: ' + body
        else:
            return 'lambda ' + concat_comma_separated(self.parameters) + ': ' + body


class Application(Expr):
    """A precedure application.

    The `operator` attribute is an instance of `Expr`.
    The `operands` attribute is a list of `Expr` instances.

    For example, the procedure application `add(2, 3)` is parsed as

    Application(Variable('add'), [Literal(2), Literal(3)])

    where `operator` is Variable('add') and `operands` are [Literal(2),
    Literal(3)].
    """

    def __init__(self, operator, operands):
        super().__init__(operator, operands)
        # the operator and the operands of the combinations。
        self.operator = operator
        self.operands = operands

    def eval(self, env):
        """For a procedure application, `eval` must recursively evaluate
        the operator and the operands of the combinations, then apply the
        resulting procedure to the resulting arguments.
        >>> new_env = global_env.copy()
        >>> new_env.update({'a': Number(3)})
        >>> expr1 = Application(Variable('add'), [Literal(2), Variable('a')])
        >>> expr1.eval(new_env)
        Number(5)
        >>> expr2 = Application(Lambda(['x'], Application(Variable('add'),\
        [Variable('x'), Literal(2)])), [Literal(3)])
        >>> expr2.eval(global_env)
        Number(5)
        """
        operator = self.operator.eval(env)
        operands = [operand.eval(env) for operand in self.operands]
        return operator.apply(operands)

    def __str__(self):
        function = str(self.operator)
        args = '(' + concat_comma_separated(self.operands) + ')'
        if isinstance(self.operator, Lambda):
            return '(' + function + ')' + args
        else:
            return function + args


class Value:
    """Values are the result of evaluating expressions. In an environment
    diagram, values appear on the right (either in a binding or off in
    the space to the right).

    In our interpreter, there are three types of values:
        - numbers (e.g. 42)
        - lambda procedures, which are created by lambda expressions
        - built-in procedures, which are procedures that are built into the
            interpreter (e.g. add)

    In our code, the three types of values are subclasses of the `Value` class:
    Number, LambdaProcedure, and BuiltinProcedure.
    """

    def __init__(self, *args):
        self.args = args

    def apply(self, arguments):
        """Each subclass of Value will override the apply method.

        Note that only procedures can be "applied"; attempting to apply a
        `Number` (e.g. as in 4(2, 3)) will error.

        For procedures, `arguments` is a list of `Value` instances, which are
        the arguments to the procedure. It should return a `Value` instance,
        which is the result of applying the procedure to the arguments.
        """
        raise NotImplementedError

    def __str__(self):
        """Returns a parsable and human-readable version of this value (i.e.
        the output of this value to be displayed in the interpreter).
        """
        raise NotImplementedError

    def __repr__(self):
        """Returns how the value is written in a abstract syntax tree."""
        args = '(' + concat_comma_separated([repr(arg)
                                             for arg in self.args]) + ')'
        return type(self).__name__ + args


class Number(Value):
    """A plain number. Attempting to apply a `Number` (e.g. as in 4(2, 3))
    will error.

    The `value` attribute is the Python number that this represents.
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def apply(self, arguments):
        raise TypeError("Oof! Cannot apply number {} to arguments {}".format(
            self.value, concat_comma_separated(arguments)))

    def __str__(self):
        return str(self.value)


class LambdaProcedure(Value):
    """A lambda procedure. Lambda predecedures are created in the Lambda.eval
    method. A lambda procedure is a lambda expression that knows the
    environment in which it was evaluated in.

    The `parameters` attribute is a list of variable names (a list of strings).
    The `body` attribute is an instance of `Expr`, the body of the procedure.
    The `parent` attribute is an environment, a dictionary with variable names
        (strings) as keys and instances of the class Value as values.
    """

    def __init__(self, parameters, body, parent):
        super().__init__(parameters, body, parent)
        self.parameters = parameters
        self.body = body
        # The environment in which the lambda function is defined
        self.parent = parent

    def apply(self, arguments):
        """
        >>> from pyparser import Parser
        >>> from pytokenizer import Tokenizer
        >>> tokenizer = Tokenizer()
        >>> parser = Parser()
        >>> lambda_procedure1 = parser.parse(tokenizer.tokenize('lambda x, y:\
        add(x, y)')).eval(global_env)
        >>> lambda_procedure1.apply([Number(2), Number(3)])
        Number(5)
        >>> lambda_procedure2 = parser.parse(tokenizer.tokenize('lambda x:\
        add(x, 2)')).eval(global_env)
        >>> lambda_procedure2.apply([Number(3)])
        Number(5)
        """
        if len(self.parameters) != len(arguments):
            raise TypeError("Oof! Cannot apply number {} to arguments {}".
                            format(concat_comma_separated(self.parameters),
                                   concat_comma_separated(arguments)))

        # Here we need to inherit the enclosure environment when the lambda
        # procedure is defined, which will include names of built-in
        # procedures(For example,`abs`、`add`) and the names of other variables
        # that occur
        env = self.parent.copy()

        # Then we bind the parameters to the arguments when the procedure
        # is called, which is the difference between the application of
        # a lambda procedure and a built-in procedure.
        for parameter, argument in zip(self.parameters, arguments):
            env[parameter] = argument

        return self.body.eval(env)

    def __str__(self):
        definition = Lambda(self.parameters, self.body)
        return '<function {}>'.format(definition)


class BuiltinProcedure(Value):
    """A built-in procedure. For a full list of built-in procedures, see
    `global_env` at the bottom of this file.

    The `operator` attribute is a Python function takes Python numbers and
    returns a Python number.
    """

    def __init__(self, operator):
        super().__init__(operator)
        self.operator = operator

    def apply(self, arguments):
        for arg in arguments:
            if type(arg) != Number:
                raise TypeError("Invalid arguments {} to {}".format(
                    concat_comma_separated(arguments), self))
        try:
            return Number(self.operator(*[arg.value for arg in arguments]))
        except ZeroDivisionError as e:
            print("Error message: %s" % e)

    def __str__(self):
        return '<built-in function {}>'.format(self.operator.__name__)


# The global environment that the REPL evaluates expressions in.
global_env = {
    'abs': BuiltinProcedure(operator.abs),
    'add': BuiltinProcedure(operator.add),
    'float': BuiltinProcedure(float),
    'floordiv': BuiltinProcedure(operator.floordiv),
    'int': BuiltinProcedure(int),
    'max': BuiltinProcedure(max),
    'min': BuiltinProcedure(min),
    'mod': BuiltinProcedure(operator.mod),
    'mul': BuiltinProcedure(operator.mul),
    'pow': BuiltinProcedure(pow),
    'sub': BuiltinProcedure(operator.sub),
    'truediv': BuiltinProcedure(operator.truediv),
}
