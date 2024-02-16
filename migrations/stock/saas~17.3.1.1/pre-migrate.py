from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "product_category_name")
    util.remove_column(cr, "stock_warehouse_orderpoint", "qty_to_order")
    util.remove_field(cr, "res.config.settings", "group_stock_storage_categories")
    util.remove_record(cr, "stock.group_stock_storage_categories")
    util.remove_record(cr, "stock.menu_reordering_rules_config")
    util.create_column(cr, "stock_putaway_rule", "sublocation", "varchar", default="no")

    # Putaway sublocation strategy will be set to 'closest location
    # for rules having storage category set
    query = """
        UPDATE stock_putaway_rule
           SET sublocation = 'closest_location'
         WHERE storage_category_id IS NOT NULL
    """
    cr.execute(query)
