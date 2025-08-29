from odoo.upgrade import util


def migrate(cr, version):
    # l10n_ma_ice was added in version saas~17.2
    if util.column_exists(cr, "res_partner", "l10n_ma_ice"):
        util.explode_execute(
            cr,
            """
            UPDATE res_partner
               SET company_registry = l10n_ma_ice
             WHERE l10n_ma_ice IS NOT NULL
            """,
            table="res_partner",
        )

    util.remove_field(cr, "res.partner", "l10n_ma_ice")
