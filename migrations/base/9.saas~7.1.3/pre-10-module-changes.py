# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    for x in 'user manager'.split():
        xid = 'group_lead_automation_' + x
        util.rename_xmlid(cr, 'marketing.' + xid, 'marketing_campaign.' + xid)
    util.remove_module(cr, 'marketing')

    util.remove_module(cr, 'l10n_multilang_report')     # enterprise

    util.new_module_dep(cr, 'analytic', 'report')
    util.new_module_dep(cr, 'utm', 'base')
    util.new_module_dep(cr, 'website_crm_score', 'marketing_campaign')      # enterprise

    util.remove_module_deps(cr, 'website_event_track', ('website_blog',))

    # TODO move these lines in their own scripts?
    util.remove_view(cr, 'purchase.view_account_config')
    util.remove_view(cr, 'sale.view_account_config')
    util.remove_view(cr, 'sale_service.task_type_edit_mrp_inherit')
