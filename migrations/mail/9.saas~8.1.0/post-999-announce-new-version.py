# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Emails can now be scheduled to send after a given date.
- CRM: stages can only be restricted to a specific sales team.
- Better default icon for invoicing and delivery addresses.
- Can now get user avatar through gravatar.com service.
"""

    util.announce(cr, '9.saas~8', message, format='md')

if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
