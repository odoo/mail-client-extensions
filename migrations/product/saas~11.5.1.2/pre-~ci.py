# -*- coding: utf-8 -*-
import odoo

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.on_CI():
        return
    # fix some demo data for CI
    # rename some xmlids and add new ones to match the <function> tags that are not executed during update
    # This is only done to avoid useless traceback during CI
    eb = util.expand_braces

    query = """
        WITH value_ids AS (
            SELECT l.product_tmpl_id, r.product_attribute_value_id
              FROM product_attribute_value_product_template_attribute_line_rel r
              JOIN product_template_attribute_line l
                ON l.id = r.product_template_attribute_line_id
             WHERE l.id = %s
        )
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
            SELECT %s, %s, 'product.template.attribute.value', v.id, true
              FROM product_template_attribute_value v
              JOIN value_ids
             USING (product_tmpl_id, product_attribute_value_id)
          ORDER BY v.id
             LIMIT 1
            OFFSET %s
    """

    line_1 = util.rename_xmlid(cr, *eb("product.product_{,template_}attribute_line_1"))
    if line_1:
        cr.execute(query, [line_1, "product", "product_template_attribute_value_1", 1])

    line_4 = util.rename_xmlid(cr, *eb("product.product_{,template_}attribute_line_4"))
    if line_4:
        cr.execute(query, [line_4, "product", "product_template_attribute_value_2", 1])

    util.rename_xmlid(cr, *eb("product.product_{,template_}attribute_line_2"))

    # force init mode to allow execution of `<function>` tags for child modules
    if util.module_installed(cr, "sale"):
        odoo.tools.config["init"]["sale"] = True
    if util.module_installed(cr, "website_sale"):
        odoo.tools.config["init"]["website_sale"] = True
