# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    message = """

+ New Mexican Localization
+ Odoo Studio improvements

- Next Activities:
    - Most application records (orders, invoices, project...) can now have activities attached.
      Theses activities are created to track the next action you need to do on this record, like
      sending an email, make a phone call, organise a meeting...

- Sale:
    - New coupon module: Handle coupon and promotional codes.
    - Allow to restrict payments per country.
    - New sale dashboard.
    - eCommerce: improved checkout process on mobile.

- Mass Mailing:
    - New themes.
    - Better contact management.

- Project:
    - Allow to merge two tasks.

+ Delivery:
    + Remove the Temando integration.
    + Handle Saturday delivery with Fedex.

- Usability:
    - Improve settings wizards
    - Improved notification emails.
    - Better onboarding in Invoicing app.
    - New widget to create record filter.
    - New reporting themes.

- Misc:
    + [Github](https://github.com/) integration into Discuss app.
    + [Clearbit](https://clearbit.com/) integration on Contact app.
    - Overall view changes and improvements.
    - More restricted security rules.

"""

    util.announce(cr, '10.saas~14', message, format='md')


if __name__ == '__main__':
    # odoo must be in PYTHONPATH
    def echo(_cr, version, message, format):
        print(util.md2html(message))
    util.announce = echo
    migrate(None, None)
