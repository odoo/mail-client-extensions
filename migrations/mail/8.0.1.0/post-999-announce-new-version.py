# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

{saas5_message}
- Updated Instant Messaging App: the instant messaging system is now more robust
  and is now a platform on which new kinds of instant notifications can be
  added in the future.

- Improved User Interface:

{saas5_ui}
    - New layout for advanced search: the search drawer (opened with the small arrow on the right of search boxes) will
      now appear as a header on top of the search results. It will also be open by default in reporting views, making it
      much simpler to toggle filters and groupings while analyzing reports.
    - Faster unified search box: the search box will now allow instant search for the most common
      cases, instead of waiting for auto-completed results. Auto-completion (e.g. customer names, etc.) is only
      performed on demand by clicking on the relevant search option (or using the keyboard arrows)
    - Unified menu bar allows you to switch easily between the frontend (website) and backend
    - The search results panel is now scrollable independently of the menu bars, keeping the navigation,
      search bar and view switcher always within reach.
- User signature is now in HTML format, allowing rich text.
- Odoo 8.0 is now powered by a new API (application programming interface) that makes writing new Apps
  much simpler and quicker.
"""

    saas5_message = saas5_ui = ""
    if version != "7.saas~5.1.0":
        # from older version, include saas-5 message
        saas5_ui = """\
    - Popups have been improved to be more responsive on tablets and smartphones.
    - New smart buttons: Forms views have now dynamic buttons showing statistics on related document without having to click on them.
    - Color codes are now used to display availability of manufacturing order components at a glance.
"""

        saas5_message = """\
- New Warehouse Management System:

    Odoo 8.0 comes with a complete rewrite of the warehouse management system, including
    a lot of new features.
    Schedule your pickings, packings, receptions and internal moves automatically with Odoo using
    your own routing rules. Define advanced push and pull routes to organize your warehouses and
    procurements. Here are a few of the great features available with the new WMS system:

       - Get full product traceability using the new quants inventory system
       - Use the brand new barcode-scanner interface to quickly process stock operations
       - Setup drop-shipping routes directly from suppliers to customer (see the Drop Shipping app)
       - Manage landed costs and split them among you stock moves (see the Landed Costs app)
       - Organize picking waves (see the WMS: Waves app)
       - and much more...

- New Product Configurator, allowing easy creation and management of product variants.

- Documentation generation from website forum:

    New App (Documentation) to create a full reference documentation based on questions and
    answers from the forum.
    The documentation manager defines the table of contents and any user (provided they have
    achieved sufficient karma) can add choose to include valuable questions inside any TOC entry.
    The contents can then be collaboratively improved, as for any question.

- New kanban view for documents (resumes and letters in recruitement, project documents...)

- E-Commerce:

    - Support TIN input in contact forms, useful for B2B.
    - A new dedicated Sales Team is now available to easily manage leads and eCommerce orders.

"""

    message = message.format(saas5_message=saas5_message, saas5_ui=saas5_ui)
    util.announce(cr, "8.0", message)


if __name__ == "__main__":
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.rst2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
