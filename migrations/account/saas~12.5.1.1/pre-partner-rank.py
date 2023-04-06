# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "supplier_rank", "int4")
    util.create_column(cr, "res_partner", "customer_rank", "int4")
    cr.execute(
        """
        WITH ranks AS (
            SELECT p.id as partner_id,
                   coalesce(sum((left(m.type, 3) = 'in_')::integer), 0) as supplier_rank,
                   coalesce(sum((left(m.type, 4) = 'out_')::integer), 0) as customer_rank
              FROM res_partner p
              JOIN account_move m ON p.id = m.partner_id AND m.state = 'posted'
             WHERE (p.supplier_rank IS NULL OR p.customer_rank IS NULL)
          GROUP BY p.id
        )
        UPDATE res_partner p
           SET supplier_rank = ranks.supplier_rank,
               customer_rank = ranks.customer_rank
          FROM ranks
         WHERE ranks.partner_id = p.id
    """
    )
    if util.column_exists(cr, "pos_order", "partner_id"):
        cr.execute(
            """
                WITH ranks AS (
                    SELECT partner_id, count(id) as rank
                      FROM pos_order
                  GROUP BY partner_id
                )
                UPDATE res_partner p
                   SET customer_rank = coalesce(p.customer_rank, 0) + ranks.rank
                 FROM ranks
                WHERE ranks.partner_id = p.id
            """
        )

    cr.execute(
        """
            WITH ranks AS (
                SELECT commercial_partner_id,
                       coalesce(sum(supplier_rank), 0) as supplier_rank,
                       coalesce(sum(customer_rank), 0) as customer_rank
                  FROM res_partner
                 WHERE commercial_partner_id != id
              GROUP BY commercial_partner_id
            )
            UPDATE res_partner p
               SET supplier_rank = coalesce(p.supplier_rank, 0) + ranks.supplier_rank,
                   customer_rank = coalesce(p.customer_rank, 0) + ranks.customer_rank
              FROM ranks
             WHERE ranks.commercial_partner_id = p.id
        """
    )
    # Ensure a mininal value for customers/suppliers
    query = "UPDATE res_partner SET supplier_rank = (supplier = true)::int WHERE coalesce(supplier_rank, 0) = 0"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner"))
    query = "UPDATE res_partner SET customer_rank = (customer = true)::int WHERE coalesce(customer_rank, 0) = 0"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner"))

    # Now adapt domains...
    def adapter(leaf, _, __):
        left, operator, right = leaf
        thruthy_op = "=" if bool(right) else "!="
        operator = ">" if operator == thruthy_op else "="
        return [(left, operator, 0)]

    util.update_field_usage(cr, "res.partner", "customer", "customer_rank", domain_adapter=adapter)
    util.update_field_usage(cr, "res.partner", "supplier", "supplier_rank", domain_adapter=adapter)
