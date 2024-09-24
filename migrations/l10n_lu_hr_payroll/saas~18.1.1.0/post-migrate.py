from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "l10n_lu_hr_payroll.holiday_status_situational_unemployment", util.update_record_from_xml)
