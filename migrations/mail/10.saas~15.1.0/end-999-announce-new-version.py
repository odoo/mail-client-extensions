# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    message = """

- Accounting:
    - Pro-forma invoices are now handled through sale orders
    - Add a payment receipt report that can be sent by mail
    + New "Consolidated Journals" report
    - Switzerland localisation: Support for ISR/BVR generation and postal bank accounts

- Stock:
    - No more global push/pull rules

- eCommerce:
    - New dashboard
    - New feature: Product Comparison
    - New feature: Whishlist: Let returning shoppers save products in a wishlist

+ Quality:
    + Quality checks and alerts on picking
    + General improvements

+ Studio:
    + You can now edit search views
    + Your website forms are now editable in Studio

- Usability:
    - Improve settings wizards
    - Support multi attachment upload in chatter
    - Separate personal and shared favorite filters in search views

"""

    util.announce(cr, '10.saas~15', message, format='md')


if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, format):
        print(util.md2html(message))
    util.announce = echo
    migrate(None, None)
