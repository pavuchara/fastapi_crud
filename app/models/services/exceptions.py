class ProductValidationException(BaseException):

    def __init__(self, text_error: str | None = None, *args) -> None:
        super().__init__(*args)
        self.text_error = text_error

    def __str__(self) -> str:
        return self.text_error if self.text_error else "Product field validation error!"


class UserValidationException(BaseException):

    def __init__(self, text_error: str | None = None, *args) -> None:
        super().__init__(*args)
        self.text_error = text_error

    def __str__(self) -> str:
        return self.text_error if self.text_error else "Product field validation error!"


class ReviewValidationException(BaseException):

    def __init__(self, text_error: str | None = None, *args) -> None:
        super().__init__(*args)
        self.text_error = text_error

    def __str__(self) -> str:
        return self.text_error if self.text_error else "Review field validation error!"
