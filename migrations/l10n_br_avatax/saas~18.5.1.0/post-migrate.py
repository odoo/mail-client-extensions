from odoo.upgrade import util


def migrate(cr, version):
    # remove codes from the beginning of the name
    util.explode_execute(
        cr,
        """
        UPDATE l10n_br_ncm_code AS ncm
           SET name = regexp_replace(name, '^[0-9.]+ ', '')
         WHERE name ~ '^[0-9.]+ '
        """,
        table="l10n_br_ncm_code",
        alias="ncm",
    )
