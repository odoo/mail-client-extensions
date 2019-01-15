# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    domain = util.env(cr)['ir.config_parameter'].get_param('mail.catchall.domain', 'localhost')
    message = """
- Manufacturing:
    - Major redesign of the MRP App for v10
    - New MRP Apps: Quality Control, PLM, MPS, Work Orders planning, Equipments & Maintenance
- Expenses: updated App with many improvements, support for submitting batch expenses as Expense Reports, creation via email, etc.
- Accounting: new TaxCloud App, to compute sales tax based on customer address in the USA
- Events: new App to add barcodes on printed badges for faster check-in
- Point of Sale: manage lots/serial numbers directly from POS
- eCommerce, Sales & Payments:
    - Improved checkout process (design + extensibility)
    - "Sold out" warnings can be displayed on the Shop
    - B2C/B2B tax display option (show prices with/without taxes)
    - Customers: new "company name" field on customers for simpler B2C signup
    - Payment methods can now be configured to generate paid invoices after acquirer confirmation
- Mailing-list: unsubscription now possible without logging in
- Project: improved front-end portal (issue rating + view projects)
- Usability:
    - Chatter: source document is now a link in the message timeline
    - New advanced search operator for date range: "between <begin> and <end>"
    - QWeb templates are now compiled, website rendering is much faster
    - Basic python error detection in server actions
    - Many smaller performance improvements
- And much more...
""".format(domain=domain)

    util.announce(cr, '9.saas~12', message, format='md')

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    # Use version < saas~10, because syspath is not initialized with `OdooHook`,
    # so no `odoo` module importable (it will import odoo.py instead).
    def echo(_cr, version, message, format):
        print(util.md2html(message))
    util.announce = echo
    migrate(None, None)
