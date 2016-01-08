# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Delivery: Handle [HS Code](https://en.wikipedia.org/wiki/Harmonized_System) for supported carriers.
- HR Recruitment: Stages can be restricted to a specific job position.
- Expense: Can specify account on which the expense should be applied.
"""

    util.announce(cr, '9.saas~9', message, format='md')

if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
