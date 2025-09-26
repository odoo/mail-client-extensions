from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "street_number", "varchar")
    util.create_column(cr, "res_partner", "street_number2", "varchar")
    if util.create_column(cr, "res_partner", "street_name", "varchar"):
        # when this module is auto-installed we need to compute the columns
        util.explode_execute(
            cr,
            r"""
            UPDATE res_partner p
               SET street_name = trim(m[1]),
                   street_number = trim(m[2]),
                   street_number2 = m[3]
              FROM res_partner p2,
                   regexp_match(p2.street, '^(.*?)(\s[0-9]\S*)?(?: - (.+))?$') AS m
             WHERE p.id = p2.id
               AND m IS NOT NULL
            """,
            table="res_partner",
            alias="p",
        )
