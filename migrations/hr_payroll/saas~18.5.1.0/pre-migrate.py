from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_payroll.menu_report_payroll")
    util.remove_field(cr, "hr.salary.rule", "appears_on_payroll_report")
    util.remove_field(cr, "res.config.settings", "module_hr_payroll_account")
    util.remove_model(cr, "hr.payroll.report")
    util.remove_field(cr, "hr.payslip", "has_refund_slip")
    util.remove_field(cr, "hr.rule.parameter", "current_value")

    util.create_column(cr, "hr_payslip", "done_date", "timestamp without time zone")
    util.create_column(cr, "hr_payslip", "is_refunded", "bool", default=False)
    util.create_column(cr, "hr_payslip", "is_refund_payslip", "bool", default=False)
    util.create_column(cr, "hr_payslip", "origin_payslip_id", "int4")
    util.create_column(cr, "hr_payslip", "has_wrong_data", "bool", default=False)
    util.create_column(cr, "hr_payslip", "is_wrong_version", "bool", default=False)
    util.create_column(cr, "hr_salary_attachment", "duration_type", "varchar", default="one")

    util.explode_execute(
        cr,
        """
        UPDATE hr_payslip payslip
           SET done_date = COALESCE(paid_date, write_date)
         WHERE state IN ('done', 'paid')
        """,
        table="hr_payslip",
        alias="payslip",
    )

    util.explode_execute(
        cr,
        """
        UPDATE hr_payslip origin
           SET is_refunded = TRUE
          FROM hr_payslip refund
         WHERE refund.employee_id = origin.employee_id
           AND refund.date_from = origin.date_from
           AND refund.date_to = origin.date_to
           AND refund.version_id = origin.version_id
           AND refund.struct_id = origin.struct_id
           AND refund.credit_note
           AND refund.state != 'cancel'
           AND origin.credit_note IS NOT TRUE
           AND origin.state IN ('done', 'paid')
        """,
        table="hr_payslip",
        alias="origin",
    )

    util.explode_execute(
        cr,
        """
        UPDATE hr_payslip refund
           SET origin_payslip_id = origin.id,
               is_refund_payslip = TRUE
          FROM hr_payslip origin
         WHERE origin.employee_id = refund.employee_id
           AND origin.date_from = refund.date_from
           AND origin.date_to = refund.date_to
           AND origin.version_id = refund.version_id
           AND origin.struct_id = refund.struct_id
           AND refund.credit_note
           AND refund.state != 'cancel'
           AND origin.credit_note IS NOT TRUE
           AND origin.state IN ('done', 'paid')
        """,
        table="hr_payslip",
        alias="refund",
    )

    util.explode_execute(
        cr,
        """
        UPDATE hr_payslip target
           SET has_wrong_data = TRUE
          FROM hr_version version
         WHERE target.version_id = version.id
           AND version.last_modified_date > target.done_date
           AND target.state IN ('done', 'paid')
        """,
        table="hr_payslip",
        alias="target",
    )

    util.explode_execute(
        cr,
        """
        WITH correct_versions AS (
              SELECT ps.id AS payslip_id,
                     COALESCE(version_on_date.id, fallback_version.id) AS correct_version_id
                FROM hr_payslip ps
        JOIN LATERAL (
                SELECT v.id
                  FROM hr_version v
                 WHERE v.employee_id = ps.employee_id
                   AND v.date_version <= ps.date_from
                 ORDER BY v.date_version DESC
                 LIMIT 1
            ) AS version_on_date ON TRUE
   LEFT JOIN LATERAL (
                SELECT v.id
                  FROM hr_version v
                 WHERE v.employee_id = ps.employee_id
                 ORDER BY v.date_version ASC
                 LIMIT 1
            ) AS fallback_version ON version_on_date.id IS NULL
        )
        UPDATE hr_payslip target
           SET is_wrong_version = TRUE
          FROM correct_versions cv
         WHERE target.id = cv.payslip_id
           AND target.version_id IS DISTINCT FROM cv.correct_version_id
        """,
        table="hr_payslip",
        alias="target",
    )

    util.remove_record(cr, "hr_payroll.hr_work_entry_validated")
    util.remove_view(cr, "hr_payroll.hr_payroll_structure_view_kanban")
    util.remove_view(cr, "hr_payroll.hr_salary_rule_view_kanban")
    util.remove_act_window_view_mode(cr, "hr.payroll.structure", "kanban")
    util.remove_act_window_view_mode(cr, "hr.salary.rule", "kanban")

    xmlids = [
        "hr_payroll.default_assignment_of_salary_rule",
        "hr_payroll.default_attachment_of_salary_rule",
        "hr_payroll.default_basic_salary_rule",
        "hr_payroll.default_child_support",
        "hr_payroll.default_deduction_salary_rule",
        "hr_payroll.default_gross_salary_rule",
        "hr_payroll.default_net_salary",
        "hr_payroll.default_reimbursement_salary_rule",
        "hr_payroll.hr_salary_rule_13th_month_salary",
        "hr_payroll.hr_salary_rule_ca_gravie",
        "hr_payroll.hr_salary_rule_convanceallowance1",
        "hr_payroll.hr_salary_rule_houserentallowance1",
        "hr_payroll.hr_salary_rule_meal_voucher",
        "hr_payroll.hr_salary_rule_professionaltax1",
        "hr_payroll.hr_salary_rule_providentfund1",
        "hr_payroll.hr_salary_rule_sum_alw_category",
    ]
    for xmlid in xmlids:
        util.force_noupdate(cr, xmlid, noupdate=False)

    util.remove_model(cr, "hr.payroll.master.report")

    util.remove_view(cr, "hr_payroll.hr_payroll_master_report_view_list")
    util.remove_view(cr, "hr_payroll.hr_payroll_master_report_view_form")

    util.remove_menus(cr, [util.ref(cr, "hr_payroll.hr_menu_salary_attachments")])

    util.remove_field(cr, "hr.salary.rule", "preview_currency_position")
    util.remove_field(cr, "hr.salary.rule", "preview_currency_symbol")

    # Salary rule range condition removal and migration
    cr.execute("""
        UPDATE hr_salary_rule
        SET condition_select = 'python',
            condition_python = 'result = ' ||
                COALESCE(condition_range_min::text, '0.0') || ' <= ' ||
                COALESCE(condition_range, '0.0') || ' <= ' ||
                COALESCE(condition_range_max::text, '0.0')
        WHERE condition_select = 'range'
    """)

    util.remove_field(cr, "hr.salary.rule", "condition_range_max")
    util.remove_field(cr, "hr.salary.rule", "condition_range_min")
    util.remove_field(cr, "hr.salary.rule", "condition_range")

    util.change_field_selection_values(
        cr,
        "hr.payslip",
        "state",
        {
            "verify": "draft",
            "done": "validated",
        },
    )
    util.change_field_selection_values(
        cr,
        "hr.payslip.run",
        "state",
        {
            "01_draft": "01_ready",
            "02_verify": "01_ready",
            "03_close": "02_close",
            "04_paid": "03_paid",
            "05_cancel": "04_cancel",
        },
    )
    util.remove_field(cr, "hr.payslip", "warning_message")
    util.remove_view(cr, "hr_payroll_holidays.hr_payslip_view_form")

    util.create_column(cr, "hr_payslip", "error_count", "integer")
    util.create_column(cr, "hr_payslip", "warning_count", "integer")
    util.create_column(cr, "hr_payslip", "issues", "jsonb")
    util.create_column(cr, "hr_payslip", "state_display", "varchar")

    cr.execute(r"""
        UPDATE hr_salary_attachment
           SET duration_type = 'unlimited'
         WHERE no_end_date = TRUE
        """)
    util.remove_field(cr, "hr.salary.attachment", "no_end_date")

    state_mapping = {
        "cancel": "close",
    }

    util.change_field_selection_values(cr, "hr.salary.attachment", "state", state_mapping)
