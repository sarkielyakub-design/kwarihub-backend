"""KWARIHUB - vendors - constants.py"""
from enum import Enum


class VendorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"