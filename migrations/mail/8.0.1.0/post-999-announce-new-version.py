# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

{saas5_message}
- Better Instant Messaging.
- Faster and Improved Search view: Search drawer now appears on top of the results, and is open
  by default in reporting views
- Improved User Interface:
{saas5_ui}
    - Unified menu bar allows you to switch easily between the frontend (website) and backend
    - Results panel is now scrollable independently of the menu bars, keeping the navigation,
      search bar and view switcher always within reach.
- User signature is now in HTML.
- New development API.
- Remove support for Outlook and Thunderbird plugins
"""

    saas5_message = saas5_ui = ""
    if version != '7.saas~5.1.0':
        # from older version, include saas-5 message
        saas5_ui = """\
    - Popups has changed to be more responsive on tablets and smartphones.
    - New Stat Buttons: Forms views have now dynamic buttons showing some statistics abouts linked models.
    - Color code to check in one look availability of components in an MRP order.
"""

        saas5_message = """\
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
"""

    message = message.format(saas5_message=saas5_message, saas5_ui=saas5_ui)
    util.announce(cr, '8.0', message)

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print util.rst2html(message)
    util.announce = echo
    migrate(None, None)
