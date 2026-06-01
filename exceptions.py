class ButtonError(Exception):
    pass


class MenuButtonNotFoundError(ButtonError):
    pass


class DeleteButtonNotFoundError(ButtonError):
    pass


class ConfirmButtonNotFoundError(ButtonError):
    pass
