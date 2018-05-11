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


def get_routes():
    return []


# TODO: This is not needed
def run(taskview, jc):
    cmd = jc.getFunction()
    if cmd not in command_map:
        err = "invalid command specified %s" % (cmd)
        taskview.log(err)
        jc.setError(err)
        return jc

    args = [taskview]
    args.append(jc)
    return command_map[cmd]["function"](*args)
