from ..schema import get_session
from ..schema.roles import Role
from ..utils.error import BlebotError

MODULES = {
    "list": "rsvp",
    "rsvp": "rsvp",
    "ditch": "rsvp",
    "create": "rsvp",
    "delete": "rsvp"
}

def check_role(command, message):
    server, channel = message.server, message.channel

    # Check if the role exists
    session = get_session(message.server.id)

    role = session.query(Role).filter(
        Role.channel == channel.id
    ).first()

    module =  MODULES.get(command, None)
    if not module:
        raise BlebotError("The command: `{command}` is not a valid command.")

    if not role or not role.modules or module not in role.modules:
        raise BlebotError("The command:`{command}` is not enabled for this channel! \nPlease assign it by using `/enable #{channel} {module}`".format(
            channel=message.channel,
            command=command,
            module=module
        ))
    return role
