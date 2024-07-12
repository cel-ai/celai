from dataclasses import dataclass


@dataclass
class ClientCommand:
    command: str
    args: list


def parse_client_command(message: str) -> ClientCommand:
    """ Will try to match a client command inside a message. A client command begins with a '/' character.
    for example /reset all will be parsed as command='reset' and args={'all'}
    Another example /phone set +1232342342 will be parsed as command='phone' and args={'set', '+1232342342'}
    """
    if message.startswith("/"):
        parts = message.split(" ")
        command = parts[0][1:]
        args = []
        if len(parts) > 1:
            args = parts[1:]
        return ClientCommand(command, args)

    else:
        return None
        


if __name__ == "__main__":
    print(parse_client_command("/reset all"))
    print(parse_client_command("/phone set +1232342342"))


