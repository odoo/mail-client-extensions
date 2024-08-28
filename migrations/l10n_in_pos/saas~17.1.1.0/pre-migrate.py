from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_order_line", "l10n_in_hsn_code", "varchar")
    util.explode_execute(
        cr,
        """
        WITH lines AS (
           SELECT pol.id as line_id,
                  pt.l10n_in_hsn_code
             FROM pos_order_line pol
             JOIN res_company c
               ON c.id = pol.company_id
             JOIN res_country co
               ON co.id = c.account_fiscal_country_id
             JOIN product_product p
               ON p.id = pol.product_id
             JOIN product_template pt
               ON pt.id = p.product_tmpl_id
            WHERE co.code = 'IN'
              AND pt.l10n_in_hsn_code IS NOT NULL
              AND {parallel_filter}
       )
       UPDATE pos_order_line pol
          SET l10n_in_hsn_code = lines.l10n_in_hsn_code
         FROM lines
        WHERE lines.line_id = pol.id
        """,
        table="pos_order_line",
        alias="pol",
    )
