# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in Markdown \o/
    message = """

### New eCommerce and CMS features

- New website editor with improved usability and more flexibility
- Website versioning: prepare multiple versions of your website and [switch between them in one click](https://www.youtube.com/watch?v=NfEiciSSTFk)
- Easy [A/B testing of your website](https://www.youtube.com/watch?v=IK-drNLuGks) based on multiple versions
- New CMS building blocks, such as the "Table" block for displaying detailed product info or the "Gallery" block for showcasing pictures
- Website Link Tracker to create shortened and trackable URLs for marketing purposes

### Point of Sales updated

- POS Restaurant to layout restaurant floor, navigate orders per table, print orders on kitchen printer, print bills before they are paid and split bills into different orders per guestt
- POS Receipt Reprinting to let cashiers manually reprint POS receipts
- POS Discounts for manual cashier discounts
- POS Loyalty Program with customer rewards
- Improved and unified POS interface
- Waitress tip management
- Initial product category selection
- Optimized session startup with many products

### New features

- Advanced barcode nomenclatures for Point of Sale and Warehouse Management System
- Project Management: customized pipeline stages with personal tooltips and custom red/green button semantics
- Instant messaging: support for canned responses and emoji emoticons
- Customer Rating system available for Project Tasks, Issues and LiveChat sessions (look for "Rating" apps)
- Bank Statements: new Apps to import your statements in OFX and QIF formats
- Intercompany: new App to automatically mirror orders and invoices in multi-company setups
- New Slides application to publish videos, presentations and documents, complete with channels, filters, tags and statistics
- Updated Forum App with option to share links and start regular discussion threads

### User experience improvements

- Flat design look for backend interface
- Streamlined search views with smoother integration in pivot tables and graphs, and dynamic grouping
- New responsive DatePicker widget
- Onboarding tips to help new users get familiar with Odoo features

"""

    util.announce(cr, "8.saas~6", message, format="md")


if __name__ == "__main__":
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.md2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
