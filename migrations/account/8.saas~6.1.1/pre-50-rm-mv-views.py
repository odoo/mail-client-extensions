# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = {
        'view_account_analytic_entries_search': 'view_account_analytic_entries_pivot',
        'view_account_entries_report_graph': 'view_account_entries_report_pivot',
        'view_account_invoice_report_graph': 'view_account_invoice_report_pivot',
    }
    for f, t in renames.items():
        res_id = util.rename_xmlid(cr, 'account.' + f, 'account.' + t)

        if res_id:
            cr.execute("UPDATE ir_ui_view SET type = %s WHERE id = %s",
                       ('pivot', res_id))

    util.remove_view(cr, 'account.sequence_inherit_form')

    # and sql views
    util.drop_depending_views(cr, 'account_account', 'type')
    util.drop_depending_views(cr, 'account_invoice', 'state')
