# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Timesheets: entries now recorded and managed directly per project or task (formerly per analytic account)
- Project:
    + Dashboard is now based on your favorite projects.
      Be sure to star some projects to see them.
    + Stages can now be configured with automatic mail notifications (templates)
- Generic:
    + new multi-company switcher in top bar
    + terminology changes (a.o. Supplier -> Vendor)
- POS: fiscal position automatically set on customers
- CRM: claims have been converted to project issues
- Stock: option to manage multiple locations without multiple warehouses
- Sales:
    + dedicated search views for quotations and orders
    + sales analysis per product category
- Delivery:
    + Allow to mark carriers' credentials as production/test ready.
    + Multiple improvements in cost management/rating
- Accounting: multi-level hierarchy in trial balance
- Mail: better handling of inline images in incoming emails

"""

    util.announce(cr, "9.saas~10", message, format="md", pluses_for_enterprise=False)


if __name__ == "__main__":
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, format):
        print(util.md2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
