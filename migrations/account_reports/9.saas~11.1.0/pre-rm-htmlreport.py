# -*- coding: utf-8 -*-
from openerp.tools.safe_eval import safe_eval
from openerp.addons.base.maintenance.migrations import util

def rm_htmlreport(cr, *xmlids):
    ids = [util.ref(cr, x) for x in xmlids]
    actions = []
    cr.execute("SELECT id, context FROM ir_act_client WHERE tag = 'account_report_generic'")
    for act_id, context in cr.fetchall():
        context = safe_eval(context or '{}')
        if context.get('model') == 'account.financial.html.report' and context.get('id') in ids:
            actions.append(act_id)

    if actions:
        cr.execute("DELETE FROM ir_act_client WHERE id = ANY(%s)", [actions])
        cr.execute("DELETE FROM ir_ui_menu WHERE action IN %s",
                   [tuple("ir.actions.client,%d" % a for a in actions)])

    for r in xmlids:
        util.remove_record(cr, r)

def migrate(cr, version):
    rm_htmlreport(
        cr,
        'account_reports.account_financial_report_agedpayable0',
        'account_reports.account_financial_report_agedreceivable0',
    )
