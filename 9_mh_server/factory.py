"""
    Command Factory
    ===============

    This serves as a nifty way to define the arguments that can be used
    to call functions defined in server_pawn which is referred to as the
    `actor` when the command handler runs commands.

    Example Usage:
    --------------

    class Foo:
        ...
        @factory.register("debug_cmd", "debug_cmd description",
            ["x", int, 0, "x-val"],
            ["y", int, 0, "y-val"],
            ["z", int, 0, "z-val"])
        def debug_cmd(self, x, y, z):
            print "Got debug cmd: ", x, y, z

    f = Foo()
    factory.run("debug_cmd", f, "1", "2", "3")

    # Or from within F:
    factory.run("debug_cmd", self, "1" ...)
"""

command_map = dict()

def register(name, description, *arg_descs):
    """ Decorator for functions which we want to expose commands for.
    """
    if arg_descs == None:
        arg_descs = []

    def wrapper(fn):
        for n in [name] if isinstance(name, str) else name:
            if n not in command_map:
                print("MHServer :: Registering command :: %s" % (n))
                command_map[n] = {
                    "function":    fn,
                    "arguments":   arg_descs,
                    "description": description,
                }
        return fn
    return wrapper


def run(tv, cmd, args):
    if cmd not in command_map:
        tv.log("invalid command specified %s" % (cmd))

    # Embed the class as the first argument, this is essentially like
    # calling `tv.<method>`.
    fwd_args  = [tv]
    entry     = command_map[cmd]
    function  = entry["function"]
    arguments = entry["arguments"]
    i         = 0

    print args
    if len(args) > len(arguments):
        args = args[:len(arguments)]
    print args

    for i in range(len(args)):
        print "i == %d" % (i)
        # Edge case for no arguments, shows up as empty list.
        if i == 0 and args[i] == []:
            break

        arg, desc    = args[i], arguments[i]
        n, t, de, di = desc[0], desc[1], desc[2], desc[3]

        try:
            if t == int:
                fwd_args.append(int(arg))
            elif t == float:
                fwd_args.append(float(arg))
            elif t == bool:
                if arg in ["t", "T", "true", "TRUE", "True", 1, "1", "Yes", "Y", "yes", "YES", "y", True]:
                    fwd_args.append(True)
                else:
                    fwd_args.append(False)
            else:
                fwd_args.append(arg)
        except Exception as e:
            # TODO (sabhiram) : Do we fail here? Do we pass the default value?
            tv.log("WARNING: Command %s has argument exception with arg %s -- using default!" % (cmd, n))
            fwd_args.append(de)
            pass

    print "I == %d about to invoke" % (i)
    while i < len(arguments):
        # Append default argument for missing / optional param.
        fwd_args.append(arguments[i][2])
        i += 1

    return function(*fwd_args)
