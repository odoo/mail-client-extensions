# -*- coding: utf-8 -*-
from openerp.release import series

from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if series[0] == "8":
        # pass from saas-4 to 8 directly, do not output saas-5 message (will
        # be included in 8.0 message)
        return

    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

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
    achieved sufficient karma) can add a question to an entry of this TOC. The contents
    can then be collaboratively improved.

- New kanban view for documents (resumes and letters in recruitement, project documents...)

- E-Commerce:

    - Support TIN input in contact forms for B2B.
    - Dedicated sales team to easily manage leads and orders.

- Improved User Interface:

    - Popups have been improved to be more responsive on tablets and smartphones.
    - New smart buttons: many forms views (e.g. on customers) now have dynamic buttons showing
      statistics on related documents without having to click on them.
    - Color codes are now used to display availability of manufacturing order components at a glance.
"""
    util.announce(cr, "7.saas~5", message)


if __name__ == "__main__":
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.rst2html(message))  # noqa: T201

    series = "pass"
    util.announce = echo
    migrate(None, None)
