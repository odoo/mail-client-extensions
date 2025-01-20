from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company
           SET tax_calculation_rounding_method = 'round_globally'
         WHERE account_fiscal_country_id = %s
        """,
        [util.ref(cr, "base.mx")],
    )
