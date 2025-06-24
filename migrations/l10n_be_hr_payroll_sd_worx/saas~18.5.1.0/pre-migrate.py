from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_view(cr, "l10n_be_hr_payroll_sd_worx.l10n_be_export_sdworx_leaves_wizard_view_form")
    util.rename_model(cr, "l10n_be.export.sdworx.leaves.wizard", "l10n.be.hr.payroll.export.sdworx")
    util.remove_field(cr, "l10n.be.hr.payroll.export.sdworx", "leave_ids")
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll_sd_worx.hr_employee_form_l10n_be_hr_payroll_sd{_,}worx"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll_sd_worx.l10n_be_export_sdworx_{leaves_wizard_,}action"))
    util.rename_xmlid(
        cr, *eb("l10n_be_hr_payroll_sd_worx.menu_l10n_be_export_{sdworx_leaves_wizard,work_entries_sdworx}")
    )
