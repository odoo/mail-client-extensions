# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

## Odoo has been upgraded to version 9.0.

Read the [release notes on our website](https://www.odoo.com/page/odoo-9-release-notes).

"""

    util.announce(cr, "9.0", message, format="md", header=None)


if __name__ == "__main__":
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, *a, **kw):
        print(util.md2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
