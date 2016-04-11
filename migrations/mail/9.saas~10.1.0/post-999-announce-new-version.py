# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Claims: Claims have been converted to Project issues.
- Delivery:
    * Allow to mark carriers' credentials as production/test ready.
    * Handle carrier margin percentage on shipping price.
    * More packaging attributes: height, width, length, max weight...
- Mail: handle inline images in incomming emails.
- Project:
    * Allow to specify a mail template which will be send when a task or an issue enter a stage.
    * Users can now favorite projects.
- Timesheet: Now linked to projects.
- Backend: New Multi-Company switcher.

"""

    util.announce(cr, '9.saas~10', message, format='md')

if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, format):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
