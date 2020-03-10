# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "default_sale_order_template_id")
    util.create_column(cr, "res_company", "sale_order_template_id", "int4")

    cr.execute(
        """
        WITH defaults AS (
            SELECT def.id AS def_id,
                   def.company_id AS def_cid,
                   tmpl.id as tmpl_id,
                   tmpl.company_id as tmpl_cid
              FROM ir_default def
              JOIN ir_model_fields field ON field.id=def.field_id
              JOIN sale_order_template tmpl on tmpl.id=def.json_value::int
             WHERE field.model = 'sale.order'
               AND field.name = 'sale_order_template_id'
               AND def.user_id IS NULL
               AND def.condition IS NULL
               AND def.json_value IS NOT NULL
          ORDER BY def_cid,def_id
        )
        UPDATE res_company comp
           SET sale_order_template_id=tmpl_id
          FROM defaults def
         WHERE comp.sale_order_template_id IS NULL
           AND (def_cid IS NULL OR comp.id = def_cid)
           AND (tmpl_cid IS NULL OR tmpl_cid = def_cid)
    """
    )
    cr.execute(
        """
        DELETE FROM ir_default
        WHERE id IN (
            SELECT def.id
              FROM ir_default def
              JOIN ir_model_fields field ON field.id=def.field_id
              JOIN sale_order_template tmpl on tmpl.id=def.json_value::int
             WHERE field.model = 'sale.order'
               AND field.name = 'sale_order_template_id'
               AND def.user_id IS NULL
               AND def.condition IS NULL
               AND def.json_value IS NOT NULL
        )
    """
    )
