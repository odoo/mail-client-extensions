from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_hr_contract")

    util.create_column(cr, "hr_job", "user_id", "int4")
    util.move_field_to_module(cr, "hr.job", "user_id", "hr_recruitment", "hr")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr.hr_menu_hr_task"),
            util.ref(cr, "hr.hr_menu_hr_my_activities"),
            util.ref(cr, "hr.hr_menu_hr_all_activities"),
        ],
    )
    util.remove_record(cr, "hr.action_hr_employee_my_activities")

    util.rename_xmlid(cr, "hr.contract_type_statutaire", "hr.contract_type_statutory", noupdate=True)
