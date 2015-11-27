# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'base.user_groups_view', silent=True)

    for fu in "group_erp_manager group_user group_multi_company".split():
        util.force_noupdate(cr, 'base.' + fu, False)

    util.remove_record(cr, 'base.multi_company_default_rule')
    util.remove_record(cr, 'base.res_currency_rule')
