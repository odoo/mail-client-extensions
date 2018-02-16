# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

## Odoo has been upgraded to version 11.0.

Read the [release notes on our website](https://www.odoo.com/page/odoo-11-release-notes).

"""

    util.announce(cr, '11.0', message, format='md', header=None)


if __name__ == '__builtin__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, *a, **kw):
        print(util.md2html(message))
    util.announce = echo
    migrate(None, None)
