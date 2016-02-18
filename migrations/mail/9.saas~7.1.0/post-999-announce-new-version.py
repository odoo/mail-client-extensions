# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

- Generic: spellchecking in many apps
- Generic: improved support for default non-english language
- Emails: default email templates cleaned up and improved
- Survey: archival of completed surveys is now available

"""

    util.announce(cr, '9.saas~7', message, format='md')

if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
