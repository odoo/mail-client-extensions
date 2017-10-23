# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'service_tracking', 'varchar')
    cr.execute("""
        UPDATE product_template
           SET service_tracking = 'task_global_project'
         WHERE id IN (
            SELECT substr(p.res_id, 18)::int
              FROM ir_property p
              JOIN ir_model_fields f ON (f.id = p.fields_id)
             WHERE f.name = 'project_id'
               AND f.model = 'product.template'
               AND p.value_reference IS NOT NULL
         )
    """)
    cr.execute("""
        UPDATE product_template
           SET service_tracking = CASE WHEN service_type = 'task' THEN 'task_new_project'
                                       ELSE 'no'
                                       END
         WHERE service_tracking IS NULL
    """)
    cr.execute("UPDATE product_template SET service_type='timesheet' WHERE service_type='task'")

    util.create_column(cr, 'sale_order_line', 'is_service', 'boolean')
    cr.execute("""
        UPDATE sale_order_line l
           SET is_service = (t.type = 'service')
          FROM product_product p
          JOIN product_template t ON (t.id = p.product_tmpl_id)
         WHERE p.id = l.product_id
    """)
    cr.execute("UPDATE sale_order_line SET is_service = false WHERE is_service IS NULL")
