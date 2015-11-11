from muu.byteplay3 import *
import dis


def muu(function):
    def compile_multiline(*args, **kwargs):
        code = Code.from_code(function.__code__)  # .co_code
        length = 0
        in_lam = 'out'

        fasts = set([])
        derefs = set([])
        closure = False
        exprs = Code.from_code((lambda: 2).__code__)
        exprs.code = []
        args = []
        z = []
        # print(code.code)
        str(code.code)
        # if somebody told me, id laugh so much but
        # if this fucking line is not here, tests fail somehow
        for opcode, value in code.code:
            # print('Q {0} {1} {2} {3}'.format(opcode, value, in_lam, length))
            if in_lam is 'out' and opcode == LOAD_GLOBAL and value == 'lam':
                length = 1
                in_lam = 'args'
            elif in_lam is 'out':
                if isinstance(opcode, int):
                    length += stack_effect(opcode,
                                           value if isinstance(value, int) else 0)

                z.append((opcode, value))
            elif in_lam == 'args':
                if opcode in [LOAD_GLOBAL, LOAD_FAST, LOAD_NAME]:
                    length += 1
                    args.append(value)
                elif opcode == CALL_FUNCTION:
                    length -= len(args)
                    in_lam = 'exprs'
            elif in_lam == 'exprs':
                if isinstance(opcode, int):
                    # print(opcode, value)
                    length += stack_effect(opcode,
                                           value if isinstance(value, int) else 0)

                if length == 1 and opcode == BINARY_SUBSCR:
                    in_lam = 'out'
                    if exprs.code[-1][0] == BUILD_TUPLE:
                        exprs.code.pop()
                    elif exprs.code[-1][0] == LOAD_CONST and type(exprs.code[-1][1]) == tuple:
                        exprs.code[-1:] = [(LOAD_CONST, t)
                                           for t in exprs.code[-1][1]]
                    exprs.code.append((RETURN_VALUE, None))
                    # print(exprs.code)
                    exprs.args = args

                    for j, (op, val) in enumerate(z):
                        if op == STORE_FAST and val in derefs:
                            z[j][0] = STORE_DEREF

                    z.extend([(LOAD_CLOSURE, der) for der in derefs])
                    if closure:
                        z.append((BUILD_TUPLE, len(derefs)))
                        exprs.freevars = derefs

                    lcode = exprs.to_code()

                    z.append((LOAD_CONST, lcode))
                    z.append((LOAD_CONST, '<lambda>'))
                    if closure:
                        z.append((MAKE_CLOSURE, 0))
                    else:
                        z.append((MAKE_FUNCTION, 0))
                elif opcode in [LOAD_GLOBAL, LOAD_NAME] and value in args:
                    exprs.code.append((LOAD_FAST, value))
                elif opcode == COMPARE_OP:
                    if exprs.code[-1][0] == LOAD_CONST and exprs.code[-1][1] < 0:
                        exprs.code[-2:] = [(exprs.code[-1][0], - exprs.code[-1][1]),
                                           (STORE_FAST, exprs.code[-2][1])]
                        fasts.add(exprs.code[-2][1])
                    elif exprs.code[-1][0] == UNARY_NEGATIVE:
                        d = 0
                        f = -2
                        if len(exprs.code) > 4:
                            for k, e in enumerate(exprs.code[:-1][::-1]):
                                if isinstance(e[0], int):
                                    d -= stack_effect(e[0], (e[1]
                                                             if isinstance(e[1], int) else 0))
                                if d == 0:
                                    break
                                f -= 1
                        else:
                            f = -2
                        # print(exprs.code, f)
                        fasts.add(exprs.code[f - 1][1])
                        exprs.code[f - 1:] = exprs.code[f:-1] +\
                            [(STORE_FAST, exprs.code[f - 1][1])]

                    else:
                        exprs.code.append((opcode, value))
                elif opcode == LOAD_FAST:
                    # now were in lambda
                    closure = True
                    exprs.code.append((LOAD_DEREF, value))
                    derefs.add(value)
                # and value in derefs:
                elif opcode in [LOAD_NAME, LOAD_FAST, LOAD_GLOBAL]:
                    if value in derefs:
                        exprs.code.append((LOAD_DEREF, value))
                    elif value in fasts:
                        exprs.code.append((LOAD_FAST, value))
                    else:
                        exprs.code.append((opcode, value))
                else:
                    exprs.code.append((opcode, value))

        code.code = z
        # print(code.code)
        function.__code__ = code.to_code()
        function._mu_compiled = True

    if not hasattr(function, '_mu_compiled'):
        compile_multiline(function)
    return function


# class MultilineLambda(CallSubscriptMacro):
#   pattern 'lam', {Call: 'args', Subscript: 'exprs'}

#   def expand(self):
#       return Lambda

    # lam(x)(x+2)
    # lam(x)[x + 2]
    # lam(x)[
    #   x + 4,
    #   x
    # ]

    # 'lam','args', 'exprs'
