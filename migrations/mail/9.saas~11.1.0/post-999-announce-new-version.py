# -*- coding: utf-8 -*-
import re
from openerp.addons.base.maintenance.migrations import util     # noqa

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    # NOTE `+` points are for enterprise only
    message = """

- Discuss:
    - Support commands in channels. Commands starts with /. Try typing "/help" in this channel.
    - Support mentiosn in chat windows (@ keyword).
    - Display count of starred messages.

- Import: filter the possible fields on which a column can be imported based on data type.
- New payment providers: payumoney and stripe.

- Timesheets:
    - project_timesheet, sale_service: support for project sub-tasks.
    + Grid view for timesheets.

- Accounting:
    + Possibility to import bank statements via CSV and CAMT.053 XML files.
    - New analytic accounting analysis report.

+ Contracts: New cohort analysis.

- Website:
    - New dashboards.
    - You can now set the website favicon.

- Misc:
    - You can now set warnings on partners about sales, purchases, invoices and picking without
      the `warning` module, which required installing `sale`, `purchase`, `account` and `stock` modules.

- Usability:
    - New main menu: Products.
    - WMS: picking form improvement, changes in delivery slips.
    - Onboarding for Subscription app.
    + Type something in the home page and get a quick search bar to find menu you are looking for.
    + Keyboard shortcuts detailed on the top right menu from the home page.
    - Many performance improvements.
"""

    plus_re = r'^(\s*)\+ (.+)\n'
    replacement = r'\1- \2\n' if util.has_enterprise() else ''
    message = re.sub(plus_re, replacement, message, flags=re.M)

    util.announce(cr, '9.saas~11', message, format='md')

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    # Use version < saas~10, because syspath is not initialized with `OdooHook`,
    # so no `odoo` module importable (it will import odoo.py instead).
    def echo(_cr, version, message, format):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
