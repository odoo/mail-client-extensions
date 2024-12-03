from odoo.upgrade import util


def migrate(cr, version):
    if util.version_gte("saas~18.3"):
        return

    util.if_unchanged(cr, "l10n_sk_hr_payroll.hr_leave_type_maternity", util.update_record_from_xml)
