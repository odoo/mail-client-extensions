from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_between("18.0", "19.0"):
        return
    util.make_field_non_stored(cr, "hr.payroll.payment.report.wizard", "company_id")
