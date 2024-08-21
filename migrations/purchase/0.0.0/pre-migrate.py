from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "purchase_order", "currency_rate"):
        util.explode_execute(
            cr,
            """
            UPDATE purchase_order po
               SET currency_rate = 1.0
              FROM res_company c
             WHERE po.company_id = c.id
               AND po.currency_id = c.currency_id
               AND po.currency_rate IS NULL
            """,
            table="purchase_order",
            alias="po",
        )
