from odoo.upgrade import util


def migrate(cr, version):
    util.merge_model(
        cr,
        "hr.expense.sheet",
        "hr.expense",
        fields_mapping={
            "user_id": "manager_id",
        },
        drop_table=False,
    )

    util.change_field_selection_values(
        cr,
        "hr.expense",
        "approval_state",
        {
            "submit": "submitted",
            "approve": "approved",
            "cancel": "refused",
        },
    )
    util.change_field_selection_values(
        cr,
        "hr.expense",
        "state",
        {
            "draft": "draft",
            "reported": "draft",
            "submitted": "submitted",
            "refused": "refused",
            # Placeholder value, those will be recomputed later with the states 'approved', 'posted', 'in_payment', 'paid'
            "done": "approved",
            "approved": "approved",
        },
    )

    cr.execute("SELECT id FROM hr_expense WHERE hr_expense.state = 'approved'")
    util.recompute_fields(cr, "hr.expense", ["state"], ids=tuple(expense_id for (expense_id,) in cr.fetchall()))

    cr.execute("SELECT id FROM hr_employee WHERE hr_employee.expense_manager_id IS NULL")
    util.recompute_fields(
        cr, "hr.employee", ["expense_manager_id"], ids=tuple(employee_id for (employee_id,) in cr.fetchall())
    )

    util.remove_field(cr, "hr.expense", "sheet_id")
    util.if_unchanged(cr, "hr_expense.mail_act_expense_approval", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_approved", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_refused", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_paid", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_reset", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_entry_delete", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.mt_expense_entry_draft", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.hr_expense_template_refuse_reason", util.update_record_from_xml)

    cr.execute("DROP TABLE hr_expense_sheet")
