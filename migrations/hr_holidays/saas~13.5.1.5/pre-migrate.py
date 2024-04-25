from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr_holidays.hr_holidays_menu_manager_approve"),
            util.ref(cr, "hr_holidays.hr_holidays_menu_manager_all"),
            util.ref(cr, "hr_holidays.menu_open_employee_leave"),
            util.ref(cr, "hr_holidays.hr_holidays_menu_manager_all_allocations"),
            util.ref(cr, "hr_holidays.hr_holidays_menu_manager_payroll"),
            util.ref(cr, "hr_holidays.hr_holidays_menu_manager_payroll_to_report"),
        ],
    )

    util.remove_view(cr, "hr_holidays.hr_leave_view_form_manager_approve")
    util.remove_record(cr, "hr_holidays.hr_leave_action_all")
    util.remove_record(cr, "hr_holidays.hr_leave_action_payroll")

    util.create_column(cr, "hr_leave", "duration_display", "character varying")
    cr.execute(
        """
        UPDATE hr_leave
        SET duration_display = 'O hours'
        WHERE date_from IS NULL OR date_to IS NULL"""
    )

    util.remove_column(cr, "hr_leave", "name")
    util.remove_column(cr, "hr_leave_allocation", "name")
