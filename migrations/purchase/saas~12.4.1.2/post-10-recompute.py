from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = """
        SELECT po.id
          FROM purchase_order po
    INNER JOIN res_company c ON po.company_id=c.id
         WHERE NOT po.currency_id=c.currency_id
        """
    util.recompute_fields(cr, "purchase.order", fields=["currency_rate"], query=query)
