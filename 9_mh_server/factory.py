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
import functools

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

    entry     = command_map[cmd]
    function  = functools.partial(entry["function"], tv)
    arguments = entry["arguments"]
    i         = -1

    if len(args) > len(arguments):
        args = args[:len(arguments)]
    
    for i in range(len(args)):
        if i == 0 and args[i] == []:
            break

        arg, desc    = args[i], arguments[i]
        n, t, de, di = desc[0], desc[1], desc[2], desc[3]

        try:
            if t == int:
                function = functools.partial(function, int(arg))
            elif t == float:
                function = functools.partial(function, float(arg))
            elif t == bool:
                if arg in ["t", "T", "true", "TRUE", "True", 1, "1", "Yes", "Y", "yes", "YES", "y", True]:
                    function = functools.partial(function, True)
                else:
                    function = functools.partial(function, False)
            else:
                function = functools.partial(function, arg)
        except Exception as e:
            tv.log("WARNING: Command %s has argument exception with arg %s -- using default!" % (cmd, n))
            function = functools.partial(function, de)
            pass

    i += 1
    while i < len(arguments):
        function = functools.partial(function, arguments[i][2])
        i += 1

    return function()
