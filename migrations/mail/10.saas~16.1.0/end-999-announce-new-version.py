# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    message = """
- **Web UI**: Complete overhaul of the technical implementation, with increased speed, flexibility and more maintainable code
- **Service Companies**: Improved timesheet, revenue/cost computation, improved timesheet grid user experience, new timesheet dashboard
- **Website Calendar**: New App for online appointments, with sms integration, phone validation
- **Salary Package**: New App for remuneration package simulations and management
- **Organisation Chart**: New HR feature to view the position of any employee directly from the employee details
- **Invoicing & Accounting**: Improved usability for matching one payment with several invoices, better currency rate management
- **Next Activities**: New option to set up an activity flow, with automatic recommendation for the next activity
- **Manufacturing**: Improved usability for product packaging and delivery packaging, new Quality control points at Work Order level
- **Point of Sale**: Compatibility with the new customer-facing display feature of the POSBox (firmware v16)
- ... Plus a lot of fine-tuning and smaller improvements ...
"""

    util.announce(cr, '10.saas~16', message, format='md')


if __name__ == '__builtin__':
    def echo(_cr, version, message, format):
        print util.md2html(message)
    util.announce = echo
    migrate(None, None)
