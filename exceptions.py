class ButtonError(Exception):
    pass


class MenuButtonNotFoundError(ButtonError):
    pass


class DeleteButtonNotFoundError(ButtonError):
    pass


class ConfirmButtonNotFoundError(ButtonError):
    pass


class UndoRepostButtonNotFoundError(ButtonError):
    pass


class ConfirmUndoRepostButtonNotFoundError(ButtonError):
    pass


class PossibleCaptchaError(Exception):
    pass


class AllTweetsDeletedException(Exception):
    pass
