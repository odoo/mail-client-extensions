# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    sa = util.ref(cr, 'procurement.procurement_order_server_action')
    if sa:
        code = """
if env.context.get('active_model') == 'procurement.order' and env.context.get('active_ids'):
    model.browse(context['active_ids']).run()</field>
        """

        cr.execute("UPDATE ir_act_server SET code=%s WHERE id=%s", [code, sa])

    util.remove_view(cr, 'procurement.mrp_company')
