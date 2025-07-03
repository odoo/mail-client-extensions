from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_payroll.access_hr_payslip_run_employee_manager")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_with_different_company_on_contract")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_ambiguous_contract")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_new_contracts")
    util.remove_record(cr, "hr_payroll.menu_hr_payroll_employees_root")
    util.remove_record(cr, "hr_payroll.hr_menu_all_contracts")

    util.rename_field(cr, "hr.payroll.headcount.line", "contract_names", "version_names")
    util.rename_field(cr, "hr.payroll.headcount.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.worked_days", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.input", "contract_id", "version_id")
    util.rename_field(cr, "hr.payroll.edit.payslip.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.work.entry.export.employee.mixin", "contract_ids", "version_ids")
    util.rename_field(cr, "hr.payroll.index", "contract_ids", "version_ids")

    util.remove_field(cr, "hr.payslip", "contract_domain_ids")
    util.remove_field(cr, "hr.version", "salary_attachments_count")
    util.remove_field(cr, "hr.version", "employee_reference")

    util.remove_view(cr, "hr_payroll.hr_contract_view_tree")
    util.remove_view(cr, "hr_payroll.hr_contract_view_kanban")
    util.remove_view(cr, "hr_payroll.hr_contract_search_inherit")
    util.remove_view(cr, "hr_payroll.hr_contract_form_inherit")
    util.remove_view(cr, "hr_payroll.hr_payslip_run_tree")
    util.remove_view(cr, "hr_payroll.hr_payroll_employee_tree_inherit")
    util.remove_view(cr, "hr_payroll.view_hr_payslip_by_employees")

    util.remove_model(cr, "hr.payslip.employees")

    state_mapping = {
        "draft": "01_draft",
        "verify": "02_verify",
        "close": "03_close",
        "paid": "04_paid",
    }
    util.change_field_selection_values(cr, "hr.payslip.run", "state", state_mapping)

    columns = [
        "is_non_resident",
        "disabled",
    ]
    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    util.create_column(cr, "hr_payslip_run", "payslip_count", "integer")
    util.create_column(cr, "hr_payslip_run", "gross_sum", "numeric")
    util.create_column(cr, "hr_payslip_run", "net_sum", "numeric")

    cr.execute(r"""
        UPDATE hr_payslip_run AS payrun
        SET
            payslip_count = temp.count,
            gross_sum = temp.gross_sum,
            net_sum = temp.net_sum
        FROM (
            SELECT
                payslip_run_id AS payrun_id,
                COUNT(*) AS count,
                SUM(gross_wage) AS gross_sum,
                SUM(net_wage) AS net_sum
            FROM hr_payslip
            WHERE payslip_run_id IS NOT NULL
            GROUP BY payslip_run_id
        ) AS temp
        WHERE payrun.id = temp.payrun_id;
    """)

    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr_payroll.menu_hr_work_entry_report"),
            util.ref(cr, "hr_payroll.menu_hr_payroll_employee_payslips_to_pay"),
        ],
    )
