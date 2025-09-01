class DataPathError(RuntimeError):
    """Raised when data directory or file paths are invalid or missing."""


class DataValidationError(ValueError):
    """Raised when data validation fails (schema/format/content errors)."""


class DataIOError(IOError):
    """Raised when reading/parsing datasets fails (I/O or decoding)."""