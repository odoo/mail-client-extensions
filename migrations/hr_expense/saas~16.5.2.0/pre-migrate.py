from odoo.upgrade import util


def migrate(cr, version):
    # hr.expense
    util.rename_field(cr, "hr.expense", "amount_tax", "tax_amount_currency")
    util.rename_field(cr, "hr.expense", "amount_tax_company", "tax_amount")
    util.rename_field(cr, "hr.expense", "total_amount", "total_amount_currency")
    util.rename_field(cr, "hr.expense", "total_amount_company", "total_amount")
    util.rename_field(cr, "hr.expense", "unit_amount", "price_unit")
    util.rename_field(cr, "hr.expense", "untaxed_amount", "untaxed_amount_currency")
    util.rename_field(cr, "hr.expense", "label_convert_rate", "label_currency_rate")
    util.rename_field(cr, "hr.expense", "attachment_number", "nb_attachment")
    util.remove_field(cr, "hr.expense", "same_currency")
    util.remove_field(cr, "hr.expense", "unit_amount_display")
    util.remove_field(cr, "hr.expense", "reference")
    util.remove_field(cr, "hr.expense", "is_ref_editable")
    util.remove_field(cr, "hr.expense", "sheet_is_editable")
    if util.module_installed(cr, "hr_expense_extract"):
        util.move_field_to_module(cr, "hr.expense", "sample", "hr_expense", "hr_expense_extract")
    else:
        util.remove_field(cr, "hr.expense", "sample")

    # hr.expense.sheet
    util.rename_field(cr, "hr.expense.sheet", "expense_number", "nb_expense")
    util.rename_field(cr, "hr.expense.sheet", "total_amount_taxes", "total_tax_amount")
    util.remove_field(cr, "hr.expense.sheet", "address_id")

    # hr.expense.split
    util.rename_field(cr, "hr.expense.split", "amount_tax", "tax_amount_currency")
    util.rename_field(cr, "hr.expense.split", "total_amount", "total_amount_currency")

    # hr.expense.split.wizard
    util.rename_field(cr, "hr.expense.split.wizard", "total_amount", "total_amount_currency")
    util.rename_field(cr, "hr.expense.split.wizard", "total_amount_original", "total_amount_currency_original")
    util.rename_field(cr, "hr.expense.split.wizard", "total_amount_taxes", "tax_amount_currency")

    # Update the xmls
    util.if_unchanged(cr, "hr_expense.hr_expense_template_refuse_reason", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_expense.hr_expense_template_register", util.update_record_from_xml)
