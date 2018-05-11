""" command registry for various functions we want to support.
"""

################################################################################

command_map = dict()

def register(name, description, *arg_descs):
    """ Decorator for functions which we want to expose commands for.
    """
    if arg_descs == None:
        arg_descs = []

    def wrapper(fn):
        akas = []
        if isinstance(name, str):
            akas = [name]
        else:
            akas = name

        for n in akas:
            if n not in command_map:
                print "registering %s" % (n)
                command_map[n] = {
                    "function":    fn,
                    "description": description,
                }
        return fn
    return wrapper


def register_command(name, description, fn):
    if name not in command_map:
        print "Registering %s" % (name)
        command_map[name] = {
            "function": fn,
            "description": description,
        }


def run(taskview, cmd, cmd_args):
    if cmd not in command_map:
        taskview.log("invalid command specified %s" % (cmd))

    args = []
    for i in cmd_args:
        args.append(i)

    return command_map[cmd]["function"](args)
