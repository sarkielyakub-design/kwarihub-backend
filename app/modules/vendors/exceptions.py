"""KWARIHUB - vendors - exceptions.py"""
class VendorException(Exception):
    """Base vendor exception."""


class VendorNotFoundError(VendorException):
    pass


class VendorAlreadyExistsError(VendorException):
    pass


class VendorNotApprovedError(VendorException):
    pass


class VendorSuspendedError(VendorException):
    pass


class VendorApplicationRejectedError(VendorException):
    pass


class UnauthorizedVendorOrderError(VendorException):
    pass