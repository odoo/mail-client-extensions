import os

from odoo.upgrade import util


def migrate(cr, version):
    strategy = os.getenv("ODOO_UPG_183_T9", "sql")
    if strategy not in ("orm", "sql", "no"):
        raise util.UpgradeError(
            f"Invalid value for the `ODOO_UPG_183_T9` environment variable: {strategy!r}. Expected 'orm', 'sql' or 'no'"
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
