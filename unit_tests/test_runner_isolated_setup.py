from pathlib import Path

from src.models import Category
from src.runner.runner import TestRunner as Runner


def test_path_targets_isolated_account_for_nested_isolated_subcategory():
    runner = Runner(Path("tests"))
    payments = Category(name="Payments", path=Path("payments"))
    invoices = Category(name="Invoices", path=Path("payments/invoices"))
    eu_strict = Category(
        name="EU Strict Invoices",
        path=Path("payments/invoices/eu_strict_invoices"),
        account_profile={"type": "isolated"},
    )

    assert runner._path_targets_isolated_account([payments, invoices, eu_strict]) is True


def test_path_targets_isolated_account_ignores_regular_subcategories():
    runner = Runner(Path("tests"))
    payments = Category(name="Payments", path=Path("payments"))
    invoices = Category(name="Invoices", path=Path("payments/invoices"))

    assert runner._path_targets_isolated_account([payments, invoices]) is False
