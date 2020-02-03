# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Split quotation templates per product company
    env = util.env(cr)

    cr.execute(
        """
        WITH lines AS (
            SELECT sale_order_template_id, product_id FROM sale_order_template_line
         UNION ALL
            SELECT sale_order_template_id, product_id FROM sale_order_template_option
        )
        SELECT distinct sale_order_template_id,
               (array_agg(distinct t.company_id order by t.company_id))[1] as first_company_id,
               unnest((array_agg(distinct t.company_id order by t.company_id))[2:array_length(array_agg(distinct t.company_id order by t.company_id), 1)]) as other_id
          FROM lines l
    INNER JOIN product_product p on l.product_id=p.id
    INNER JOIN product_template t on p.product_tmpl_id=t.id
         WHERE t.company_id is not null
      GROUP BY sale_order_template_id
        HAVING count(DISTINCT t.company_id)>1
    """
    )
    template = env['sale.order.template']
    template_line = env['sale.order.template.line']
    option_line = env['sale.order.template.option']
    for res in cr.fetchall():
        # Copy order header
        template_id = template.browse(res[0])
        new_template_id = template_id.copy({'company_id': res[2], 'sale_order_template_option_ids': False, 'sale_order_template_line_ids': False}).id
        # Copy lines with company_id Null
        # Affect lines with new company_id
        cr.execute("UPDATE sale_order_template_line SET sale_order_template_id=%s where sale_order_template_id=%s and company_id=%s", [new_template_id, res[0], res[2]])
        template_line.search([('sale_order_template_id', '=', res[0])]).copy({'sale_order_template_id': new_template_id, 'company_id': res[2]})
        cr.execute("UPDATE sale_order_template_option SET sale_order_template_id=%s where sale_order_template_id=%s and company_id=%s", [new_template_id, res[0], res[2]])
        option_line.search([('sale_order_template_id', '=', res[0])]).copy({'sale_order_template_id': new_template_id, 'company_id': res[2]})

    cr.execute(
        """
        WITH lines AS ( SELECT sale_order_template_id, product_id FROM sale_order_template_line
                     UNION ALL
                        SELECT sale_order_template_id, product_id FROM sale_order_template_option),
        order_ids AS (SELECT distinct sale_order_template_id,t.company_id
                        FROM lines l
                  INNER JOIN product_product p on l.product_id=p.id
                  INNER JOIN product_template t on p.product_tmpl_id=t.id
                       WHERE t.company_id is not null
                    GROUP BY sale_order_template_id, company_id)
        UPDATE sale_order_template t
           SET company_id=t.company_id
          FROM order_ids o
          WHERE o.sale_order_template_id=t.id
        """
        )
    for t in ["sale_order_template_line", "sale_order_template_option"]:
        cr.execute("""
            UPDATE %s l
               SET company_id=o.company_id
              FROM sale_order_template o
             WHERE o.id=l.sale_order_template_id
            """ % t)
