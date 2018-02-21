# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    view_id = util.ref(cr, 'website_sale.reduction_code')
    new_ref_view_id = util.ref(cr, 'website_sale.total')
    cr.execute("UPDATE ir_ui_view SET inherit_id =%s WHERE id=%s", [new_ref_view_id, view_id])
