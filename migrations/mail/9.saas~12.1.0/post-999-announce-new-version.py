# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    domain = util.env(cr)['ir.config_parameter'].get_param('mail.catchall.domain', 'localhost')
    message = """
- New modules:
    - Equipements: Track equipment and manage maintenance requests.
    + Quality Control: Quality Alerts and Control Points.
    + Account TaxCloud: Compute sales tax automatically using TaxCloud based on customer address in United States.
- MRP:
    - Complete new MRP module set.
- Point of Sale: manage lot/serial number from POS.
- Expenses:
    - Can now regroup expenses in sheets.
    - New email interface: just send a picture of you ticket via email to expense@{domain} with total price in subject.
    - Improved checkout process.
    - Simple "Company Name" field on partners helps creation from checkout.
    - Option to show a warning when a product is out of stock.
    - Be more B2C friendly.
- Usability:
    - Qweb templates are now compiled, speeding up page rendering.
    - Basic python error detection in server actions.
    - Ease search of date range.
    - Many performance improvements.
""".format(domain=domain)

    util.announce(cr, '9.saas~12', message, format='md')

if __name__ == '__main__':
    # openerp must be in PYTHONPATH
    # Use version < saas~10, because syspath is not initialized with `OdooHook`,
    # so no `odoo` module importable (it will import odoo.py instead).
    def echo(_cr, version, message, format):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
