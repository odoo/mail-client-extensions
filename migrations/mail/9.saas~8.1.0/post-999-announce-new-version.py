# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

 * Emails: scheduling is possible for future email delivery
 * CRM stages: Sales teams now choose between global stages or per-team stages
 * Generic:
     - gravatar.com icon automatically retrieved when setting customer email
     - support for adding "computed" custom fields
"""

    util.announce(cr, "9.saas~8", message, format="md")


if __name__ == "__main__":
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.md2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
