# -*- coding: utf-8 -*-

def migrate(cr, version):
    # NOTE this script belong to `stock_account` module, but as this is a new module, when
    #      migrating from < saas-5, the script will not be called. Force call by placing it here.

    # move "valuation" property field from product to template
    cr.execute("""UPDATE ir_model_data
                     SET name=%s
                   WHERE model=%s
                     AND name=%s
               """, ('field_product_template_valuation', 'ir.model.fields',
                     'field_product_product_valuation'))

    cr.execute("""UPDATE ir_model_fields
                     SET model=%s,
                         model_id=(SELECT id
                                     FROM ir_model
                                    WHERE model=%s)
                   WHERE model=%s
                     AND name=%s
               RETURNING id
               """, ('product.template', 'product.template', 'product.product', 'valuation'))
    [field_id] = cr.fetchone()

    cr.execute("""update ir_property ip
                     set res_id = CONCAT('product.template,', p.product_tmpl_id)
                    from product_product p
                   where ip.res_id = CONCAT('product.product,', p.id)
                     and ip.fields_id = %s
               """, (field_id,))
