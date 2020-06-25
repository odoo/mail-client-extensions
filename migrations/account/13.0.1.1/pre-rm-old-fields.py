# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Existed in 10.0
    # https://github.com/odoo/odoo/blob/7b87212ea851518a641f65a71dc094cf88507cdc/addons/account/report/account_invoice_report.py#L72
    # removed in saas-14, odoo/odoo@5be1fabc9cf932a326034ddf951c4a6c9350b258
    # never removed in an uprade script till now.
    util.remove_field(cr, "account.invoice.report", "volume")
    util.remove_field(cr, "account.invoice.report", "weight")
