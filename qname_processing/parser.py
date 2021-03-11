#!/usr/bin/env python3

from lark import Lark, Tree, Transformer

# Crude Transformer based on examples
# https://lark-parser.readthedocs.io/en/latest/visitors.html#transformer
class transformer(Transformer):
    def SIGN(self, args):
        return args[0]

    def DIGIT(self, args):
        return args[0]

    def digits(self, args):
        return "".join(args)

    def factor(self, args):
        return args[0]

    def exponent(self, args):
        if len(args) == 1:
            return {
                "exponent": int(args[0]),
            }
        if len(args) == 2:
            return {
                "exponent": int("".join(args)),
            }

    def start(self, args):
        return args

    def term(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            return [args[0], {**args[1], **args[2]}]

    def component(self, args):
        return args[0]

    def simple_unit(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            return {**args[0], **args[1]}

    def annotatable(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            return {**args[0], **args[1]}

    def annotation(self, args):
        return args[0]

    def OPERATOR(self, args):
        return {
            "operator": args[0],
        }

    def PREFIX(self, args):
        return {
            "prefix": args[0],
        }

    def METRIC(self, args):
        return {
          "type": "metric",
          "unit": args[0],
        }

    def NON_METRIC(self, args):
        return {
          "type": "non-metric",
          "unit": "".join(args[1:-1]),
        }

    def ANNOTATION(self, args):
        return {
          "type": "non-unit",
          "unit": "".join(args)
        }


# UCUM grammar based on "Exhibit 1" https://ucum.org/ucum.html
# WARN: This is a weird hybrid of the given grammar with Lark idioms.
# If it were more Lark-y, the Transformer would be nicer.
ucum_grammar = Lark('''
SIGN: "+" | "-"
DIGIT: "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
digits: DIGIT digits | DIGIT
factor: digits
exponent: SIGN digits | digits
simple_unit: NON_METRIC
           | PREFIX? METRIC
annotatable: simple_unit exponent
           | simple_unit
component: annotatable annotation
         | annotatable
         | annotation
         | factor
term: term OPERATOR component
    | component
start: "/" term | term
annotation: "{" ANNOTATION "}"

OPERATOR: /\.|\//
NON_METRIC: "[in_i]"
PREFIX: "k" | "c" | "m"
METRIC: "m" | "g" | "s"
ANNOTATION: /[^}]+/

%ignore " "           // Disregard spaces in text
''')

for u in ["cm", "m.s", "m/s", "/g", "m2", "s-1", "[in_i]", "{cell}"]:
    tree = ucum_grammar.parse(u)
    result = transformer().transform(tree)
    if isinstance(result[0], list):
        result = result[0]
    print(u, result)

# Result:
# cm [{'prefix': 'c', 'type': 'metric', 'unit': 'm'}]
# m.s [{'type': 'metric', 'unit': 'm'}, {'operator': '.', 'type': 'metric', 'unit': 's'}]
# m/s [{'type': 'metric', 'unit': 'm'}, {'operator': '/', 'type': 'metric', 'unit': 's'}]
# /g [{'type': 'metric', 'unit': 'g'}]
# m2 [{'type': 'metric', 'unit': 'm', 'exponent': 2}]
# s-1 [{'type': 'metric', 'unit': 's', 'exponent': -1}]
# [in_i] [{'type': 'non-metric', 'unit': 'in_i'}]
# {cell} [{'type': 'non-unit', 'unit': 'cell'}]
 
