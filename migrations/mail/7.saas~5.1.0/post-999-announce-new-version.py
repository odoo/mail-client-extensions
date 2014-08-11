# -*- coding: utf-8 -*-
from openerp.release import series
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if series[0] == '8':
        # pass from saas-4 to 8 directly, do not output saas-5 message (will
        # be included in 8.0 message)
        return

    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

- New Warehouse Management System:

    < blahblahblah >

"""
    util.announce(cr, '7.saas~5', message)

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.rst2html(message)
    util.announce = echo
    migrate(None, None)
