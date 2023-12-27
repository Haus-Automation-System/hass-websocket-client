class HassException(Exception):
    def __init__(self, *args: object, detail: str = None) -> None:
        super().__init__(*args)
        self.detail = detail

    def __str__(self) -> str:
        return super().__str__() + ("\n" + self.detail if self.detail else "")


class AuthenticationError(HassException):
    pass
