# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # keep ir.filter
    util.force_noupdate(cr, 'hr_contract.contract_open', True)
    # but delete server actions & base action rules
    util.remove_record(cr, 'hr_contract.rule_contract_1_set_as_pending')
    util.remove_record(cr, 'hr_contract.rule_contract_2_set_as_pending')
    util.remove_record(cr, 'hr_contract.rule_contract_3_set_as_close')
    util.remove_record(cr, 'hr_contract.rule_contract_4_set_as_close')
    util.remove_record(cr, 'hr_contract.contract_set_as_pending')
    util.remove_record(cr, 'hr_contract.contract_set_as_close')

    util.remove_field(cr, 'base.automation', 'tgr_date_resource_field_id')
    util.remove_view(cr, 'hr_contract.view_base_action_rule_form_resource')
