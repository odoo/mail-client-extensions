# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Delivery: [Harmonized System (HS) Codes](https://en.wikipedia.org/wiki/Harmonized_System) supported for compatible carriers.
- Recruitment: choose between global stages or per-job-position stages
- Expenses: support for forcing the P&L account to use for each expense
"""

    util.announce(cr, "9.saas~9", message, format="md")


if __name__ == "__main__":
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.md2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
