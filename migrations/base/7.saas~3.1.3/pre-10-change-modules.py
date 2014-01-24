# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_module(cr, 'base_calendar', 'calendar')
    util.rename_module(cr, 'google_base_account', 'google_account')

    util.new_module_dep(cr, 'calendar', 'web_calendar')
    util.new_module_dep(cr, 'base_action_rule', 'resource')
    util.new_module_dep(cr, 'hr_contract', 'base_action_rule')

    util.remove_module(cr, 'web_shortcuts')

    deps = ('hr_recruitment', 'document')
    util.new_module(cr, 'hr_applicant_document', deps)

    util.new_module(cr, 'base_geolocalize')
    util.new_module_dep(cr, 'crm_partner_assign', 'base_geolocalize')

    util.new_module_dep(cr, 'auth_signup', 'web')

    # delivery now depend on sale_stock instead of sale and stock
    cr.execute("""DELETE FROM ir_module_module_dependency
                        WHERE module_id = (SELECT id
                                             FROM ir_module_module
                                            WHERE name=%s)
               """, ('delivery',))
    util.new_model_dep(cr, 'delivery', 'sale_stock')
