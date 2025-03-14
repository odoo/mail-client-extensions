from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll_dimona.res_config_settings_view_form")
