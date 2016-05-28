from . import rsvp
def handle_help():
    return [], """
`/delete` deletes an events. It's a shortcut for `/rsvp delete`
"""

def handle_action(command, action, args, message, extras):
    args = action + " " + args
    command = "rsvp"
    action = "delete"
    return rsvp.handle_action(command, action, args, message, extras)
