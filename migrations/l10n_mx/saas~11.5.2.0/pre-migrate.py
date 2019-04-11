# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for tax_int in ("1", "2", "3", "5", "7", "8", "9", "10", "12", "13", "14"):
        tax = "l10n_mx.tax%s" % tax_int
        tax_id = util.ref(cr, tax)
        cr.execute("delete from account_fiscal_position_tax_template where tax_dest_id=? or tax_src_id=?", (tax_id, tax_id))
        util.remove_record(cr, tax)
