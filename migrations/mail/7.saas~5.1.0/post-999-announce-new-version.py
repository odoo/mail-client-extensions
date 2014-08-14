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

    Schedule your picking, packing, receptions and internal moves automatically with Odoo using
    your own routing rules. Define push and pull rules to organize a warehouse or to manage
    product moves between several warehouses. Track in detail all stock moves, not only in your
    warehouse but wherever else it's taken as well (customers, suppliers or manufacturing
    locations).
- New Product Configurator
- Documentation generation from website forum:

    New module to generate a documentation from questions and responses from your forum.
    The documentation manager can define a table of content and any user, depending their karma,
    can link a question to an entry of this TOC.
- New kanban view of documents (resumes and letters in recruitement, project documents...)
- E-Commerce:

    - Manage TIN in contact form for B2B.
    - Dedicated salesteam to easily manage leads and orders.
- Improved User Interface:

    - Popups has changed to be more responsive on tablets and smartphones.
    - New Stat Buttons: Forms views have now dynamic buttons showing some statistics abouts linked models.
    - Color code to check in one look availability of components in an MRP order.
"""
    util.announce(cr, '7.saas~5', message)

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.rst2html(message)

    series = 'pass'     # noqa
    util.announce = echo
    migrate(None, None)
