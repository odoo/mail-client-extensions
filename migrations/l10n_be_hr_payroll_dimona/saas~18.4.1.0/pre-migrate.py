from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_be_hr_payroll_dimona.ir_cron_check_dimona")

    util.rename_field(cr, "l10n.be.dimona.wizard", "contract_id", "version_id")
