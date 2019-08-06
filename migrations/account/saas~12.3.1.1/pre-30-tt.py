# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("select module,name from ir_model_data where model='account.reconcile.model.template'")
    for module, id in cr.fetchall():
        util.remove_record(cr, "%s.%s" % (module, id))

    cr.execute("select module,name,res_id from ir_model_data where model='account.tax.template'")
    for module, id, res_id in cr.fetchall():
        cr.execute("delete from account_fiscal_position_tax_template where tax_src_id=%s", (res_id,))
        util.remove_record(cr, "%s.%s" % (module, id))
