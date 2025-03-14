from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "l10n_in_journal_id")
