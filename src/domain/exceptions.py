class AdAlreadyArchivedError(Exception):
    """Попытка изменить уже архивированное объявление."""


class InvalidAdError(ValueError):
    """Нарушение инварианта объявления (невалидные поля)."""
