from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~16.5"):
        # those records have been deleted in next version.
        util.update_record_from_xml(cr, "documents_l10n_be_hr_payroll.mail_template_individual_account")
        util.update_record_from_xml(cr, "documents_l10n_be_hr_payroll.mail_template_281_10")
        util.update_record_from_xml(cr, "documents_l10n_be_hr_payroll.mail_template_281_45")
