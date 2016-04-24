from . import rsvp
def handle_help():
    return [], """
`/list` lists the rsvp events. It's a shortcut for `/rsvp list`
"""

def handle_action(command, action, args, message, extras):
    args = action + " " + args
    command = "rsvp"
    action = "list"
    return rsvp.handle_action(command, action, args, message, extras)
