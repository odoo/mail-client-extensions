import os

from odoo.modules.db import has_unaccent

from odoo.upgrade import util


def migrate(cr, version):
    unnacent = has_unaccent(cr)
    strategy = os.getenv("ODOO_UPG_183_T9", "sql" if unnacent else "orm").lower()
    if strategy not in ("orm", "sql", "no"):
        raise util.UpgradeError(
            f"Invalid value for the `ODOO_UPG_183_T9` environment variable: {strategy!r}. Expected 'orm', 'sql' or 'no'"
        )
    if strategy == "sql" and not unnacent:
        strategy = "orm"
        util._logger.warning(
            "Missing `unaccent` PG extension, cannot use the 'sql' strategy to compute `res.partner/t9_name`. "
            "Continuing with the 'orm' strategy."
        )
    if strategy == "orm":
        util.recompute_fields(cr, "res.partner", ["t9_name"])
    elif strategy == "sql":
        util.explode_execute(
            cr,
            r"""
                UPDATE res_partner p
                   SET t9_name = ' ' || regexp_replace(
                                            translate(upper(unaccent(normalize(p.name, NFKD))),
                                                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                      '22233344455566677778889999'),
                                            '[^0-9\s]',
                                            'x',
                                            'g'
                                        )
                 WHERE p.t9_name IS NULL
                   AND NULLIF(p.name, '') IS NOT NULL
            """,
            table="res_partner",
            alias="p",
        )
    else:
        util._logger.info("skip computation of the `res.partner/t9_name` field.")
