from odoo.upgrade import util


def migrate(cr, version):
    # Remove duplicate attachments before merging models
    cr.execute(
        """
        DELETE FROM ir_attachment AS sheet_att
              USING hr_expense_sheet sheet
               JOIN hr_expense exp
                 ON exp.former_sheet_id = sheet.id
               JOIN ir_attachment exp_att
                 ON exp_att.res_model = 'hr.expense'
                AND exp_att.res_id = exp.id
              WHERE sheet_att.res_model = 'hr.expense.sheet'
                AND sheet_att.res_id = sheet.id
                AND sheet_att.checksum = exp_att.checksum
        """
    )

    util.merge_model(
        cr,
        "hr.expense.sheet",
        "hr.expense",
        fields_mapping={
            "user_id": "manager_id",
        },
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

    query = """
        UPDATE hr_expense
           SET state = 'draft', approval_state = NULL
         WHERE (
            total_amount = 0 OR total_amount_currency = 0
         )
           AND {parallel_filter}
    """
    util.explode_execute(cr, query, table="hr_expense")

    cr.execute("SELECT id FROM hr_expense WHERE state = 'done'")
    expense_ids = tuple(expense_id for (expense_id,) in cr.fetchall())
    util.change_field_selection_values(
        cr,
        "hr.expense",
        "state",
        {
            "reported": "draft",
            # Placeholder value, those will be recomputed later with the states 'approved', 'posted', 'in_payment', 'paid'
            "done": "approved",
        },
    )

    util.recompute_fields(cr, util.env(cr)["hr.expense"].with_context(mail_notrack=True), ["state"], ids=expense_ids)

    cr.execute("SELECT id FROM hr_employee WHERE expense_manager_id IS NULL")
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
