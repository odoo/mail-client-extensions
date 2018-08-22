# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _db_openerp(cr, version):
    eb = util.expand_braces
    util.new_module(
        cr, "hr_contract_salary_internal",
        deps={"hr_contract_salary", "website_hr_recruitment"},
        auto_install=True,
    )

    util.move_field_to_module(cr, "fleet.vehicle", "first_contract_date", "hr_contract_salary", "fleet")
    util.move_model(cr, "fleet.vehicle.assignation.log", "hr_contract_salary", "fleet")
    util.remove_field(cr, "fleet.vehicle.log.contract", "driver_email")

    util.remove_view(cr, "hr_contract_salary.hr_contract_view_form2")
    util.remove_view(cr, "hr_contract_salary.hr_contract_view_form4")
    util.rename_xmlid(cr, *eb("hr_contract_salary{,_internal}.action_salary_grid_modal"))
    util.rename_xmlid(cr, *eb("hr_contract_salary{,_internal}.ir_cron_update_recurring_cost_amount_depreciated"))
    util.rename_xmlid(cr, *eb("hr_contract_salary{,_internal}.fleet_service_type_odoo_sa"))
    util.rename_xmlid(cr, *eb("hr_contract_salary{,_internal}.generate_commission_plan_view_form"))
    util.rename_xmlid(cr, *eb("hr_contract_salary{,_internal}.generate_commission_plan_action"))
    util.move_model(cr, "generate.commission.plan", "hr_contract_salary", "hr_contract_salary_internal")

    cr.execute("UPDATE hr_employee SET km_home_work=vehicle_distance WHERE km_home_work IS NULL")
    util.remove_field(cr, "hr.employee", "vehicle_distance")

    util.remove_record(cr, "openerp_enterprise.partner_personal_address_rule")
    util.remove_record(cr, "openerp_enterprise.partner_personal_address_rule_officer")
    util.remove_view(cr, "openerp_enterprise.view_employee_address_form")
    util.remove_view(cr, "openerp_enterprise.custom_employee_form")

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        "8851207e-1ff9-11e0-a147-001cc0f2115e": _db_openerp,
    })
