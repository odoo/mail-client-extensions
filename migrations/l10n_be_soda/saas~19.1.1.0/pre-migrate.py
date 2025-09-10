from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_be_soda.action_open_accounting_settings")
