from odoo.upgrade import util


def migrate(cr, version):
    # Access rights migration
    msg = """
        We reworked the Attendance application. User and Officer rights no longer exists.
        Check the Attendance Settings and the Employee profile to define new settings.
        All rights set on those levels have been deleted.
    """
    util.add_to_migration_reports(msg, "Attendance", format="md")

    # Groups
    util.remove_record(cr, "hr_attendance.group_hr_attendance_kiosk")
    util.remove_record(cr, "hr_attendance.group_hr_attendance")
    util.remove_record(cr, "hr_attendance.group_hr_attendance_user")
    util.remove_record(cr, "hr_attendance.group_hr_attendance_use_pin")

    # ir.rules
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_manager")
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_overtime_manager")
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_manual")
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_employee")
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_manager_overtime_restrict")
    util.remove_record(cr, "hr_attendance.hr_attendance_rule_attendance_overtime_employee")
    util.remove_record(cr, "hr_attendance.hr_attendance_report_rule_multi_company")

    util.update_record_from_xml(cr, "base.user_demo", from_module="hr_attendance")
    util.update_record_from_xml(cr, "hr.employee_admin", from_module="hr_attendance")

    # res.config.settings
    util.remove_field(cr, "res.config.settings", "group_attendance_use_pin")

    # attendance reporting model removed
    util.remove_model(cr, "hr.attendance.report")

    # removing old actions
    util.remove_record(cr, "hr_attendance.hr_attendance_action_employee")
    util.remove_record(cr, "hr_attendance.hr_attendance_action_overview")
    util.remove_record(cr, "hr_attendance.hr_attendance_action_my_attendances")
    util.remove_record(cr, "hr_attendance.hr_attendance_action_kiosk_mode")

    # overtime_hours field on hr.attendance

    util.create_column(cr, "hr_attendance", "overtime_hours", "float8", default=0)
