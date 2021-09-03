import enum

class Role(enum.Enum):
    AIRPORT = "AIRPORT"
    BUSINESS = "BUSINESS"

class PaymentStatus(enum.Enum):
    PROCEED = "PROCEED"
    AUTHORIZED = "AUTHORIZED"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"

class Terminal(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"