from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~18.3"):
        util.if_unchanged(cr, "l10n_lu_hr_payroll.holiday_status_situational_unemployment", util.update_record_from_xml)
