from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "product_template", "is_favorite", "boolean", default=False)
    query = """
        UPDATE product_template pt
           SET is_favorite = True
         WHERE pt.priority = '1'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="product_template", alias="pt"))

    def priority_to_is_favorite_adapter(leaf, _or, _neg):
        left, op, right = leaf
        if op not in ["=", "!="]:
            return [leaf]
        new_right = right == "1"
        return [(left, op, new_right)]

    util.domains.adapt_domains(
        cr, "product.template", "priority", "is_favorite", adapter=priority_to_is_favorite_adapter
    )
    util.remove_field(cr, "product.template", "priority")

    eb = util.expand_braces
    if util.module_installed(cr, "sale"):
        util.move_field_to_module(cr, "res.config.settings", "module_sale_product_matrix", "product", "sale")
        util.move_field_to_module(cr, "res.config.settings", "group_discount_per_so_line", "product", "sale")
        util.rename_xmlid(cr, *eb("{product,sale}.group_discount_per_so_line"))
    else:
        util.remove_field(cr, "res.config.settings", "module_sale_product_matrix")
        util.remove_field(cr, "res.config.settings", "group_discount_per_so_line")
        util.remove_record(cr, "product.group_discount_per_so_line")
