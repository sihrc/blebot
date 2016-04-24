from . import rsvp
def handle_help():
    return [], """
`/create` creates an events. It's a shortcut for `/rsvp create`
"""

def handle_action(command, action, args, message, extras):
    args = action
    command = "rsvp"
    action = "create"
    return rsvp.handle_action(command, action, args, message, extras)
