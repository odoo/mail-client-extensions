from odoo.tools import sql

from odoo.upgrade import util


def migrate(cr, version):
    sql.rename_column(cr, "l10n_au_super_fund", "display_name", "name")
    util.make_field_non_stored(cr, "l10n_au.super.fund", "display_name", selectable=True)
