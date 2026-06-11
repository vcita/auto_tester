"""Setup for the isolated invoices subcategory (invoice lifecycle chain).

The create -> edit -> send -> cancel -> view tests share a single invoice, so they
must run together in one account. Running that chain in its own throwaway account
(instead of the shared payments boundary) keeps it free of tax/setting state left by
sibling subcategories and stops a flake from cascading skips across payments.

Reuses the payments-domain setup (login + invoice-picker client + required-payment
service) so the chain gets exactly the prerequisites it was written against.
"""

from playwright.sync_api import Page

from tests.salsa.payments._setup.test import setup_payments


def setup_invoices(page: Page, context: dict) -> None:
    setup_payments(page, context)
