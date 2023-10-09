import re
from datetime import date, datetime

from babel.numbers import parse_decimal
from pydantic import BaseModel, ConfigDict, field_validator


def to_decimal(val: str):
    if val[-3:] == " kr":
        return float(parse_decimal(str(val[:-3]), "se_SE"))
    else:
        raise ValueError(
            f"Invalid currency, expected suffix ' kr', got '{val}'"
        )


class IBTransaction(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        strict=True,
    )
    Datum: date
    Text: str
    Typ: str
    Budgetgrupp: str
    Belopp: float
    Saldo: float

    @field_validator("Datum", mode="before")  # noqa
    @classmethod
    def validate_datum(cls, v):
        val = v.strip()
        return datetime.strptime(val, "%Y-%m-%d").date()

    @field_validator("Belopp", mode="before")  # noqa
    @classmethod
    def validate_belopp(cls, v) -> float:
        val = v.strip()
        return to_decimal(val)

    @field_validator("Saldo", mode="before")  # noqa
    @classmethod
    def validate_saldo(cls, v) -> float:
        val = v.strip()
        return to_decimal(val)


class IBCSV(BaseModel):
    file_name: str
    account_number: str
    transactions: list[IBTransaction]

    @field_validator("account_number", mode="after")  # noqa
    @classmethod
    def validate_account_number(cls, v):
        v = v.strip()
        if not re.match(r"^\d{4}-\d{3} \d{3} \d$", v):
            raise ValueError("Invalid account number format")
        return v
