from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "l10n_be_eco_vouchers_wizard", "reference_year")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll{,_sd_worx}.l10n_be_export_sdworx_leaves_wizard_view_form"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll{,_sd_worx}.l10n_be_export_sdworx_leaves_wizard_action"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll{,_sd_worx}.menu_l10n_be_export_sdworx_leaves_wizard"))

    util.move_model(cr, "l10n_be.export.sdworx.leaves.wizard", "l10n_be_hr_payroll", "l10n_be_hr_payroll_sd_worx")

    util.remove_field(cr, "res.config.settings", "group_export_sdworx_leaves")
    util.remove_record(cr, "l10n_be_hr_payroll.group_export_sdworx_leaves")
    util.delete_unused(cr, "l10n_be_hr_payroll.work_entry_type_after_contract_public_holiday")

    for model in ["hr.work.entry.type", "res.company", "res.config.settings", "hr.employee"]:
        util.move_field_to_module(cr, model, "sdworx_code", "l10n_be_hr_payroll", "l10n_be_hr_payroll_sd_worx")
