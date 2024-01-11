from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("ALTER TABLE employee_category_rel RENAME COLUMN emp_id TO employee_id")

    util.remove_record(cr, "hr.act_employee_from_department")
    remove_fields = [
        "module_hr_attendance",
        "hr_presence_control_ip",
        "hr_presence_control_login",
        "hr_presence_control_email",
    ]
    for field in remove_fields:
        util.remove_column(cr, "res_config_settings", field)
