# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

{saas5_message}
- New developement API.

"""

    saas5_message = ""
    if version != '7.saas~5.1.0':
        # from older version, include saas-5 message
        saas5_message = """\
- New Warehouse Management System:

    < blahblahblah >

"""

    util.announce(cr, '8.0', message.format(saas5_message=saas5_message))

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.rst2html(message)
    util.announce = echo
    migrate(None, None)
