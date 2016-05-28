from . import rsvp
def handle_help():
    return """
`/ditch [event number]` ditches an existing event. It's a shortcut for `/rsvp ditch [event number]`
"""

def handle_action(command, action, args, message, extras):
    args = action + " " + args
    command = "rsvp"
    action = "ditch"
    return rsvp.handle_action(command, action, args, message, extras)
