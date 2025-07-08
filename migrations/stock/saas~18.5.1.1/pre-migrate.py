from odoo.upgrade import util


def migrate(cr, version):
    query = "UPDATE stock_picking SET create_date = date WHERE create_date IS NULL AND date IS NOT NULL"
    util.explode_execute(cr, query, table="stock_picking")
    util.update_field_usage(cr, "stock.picking", "date", "create_date")
    util.remove_field(cr, "stock.picking", "date")
    if util.module_installed(cr, "stock_sms"):
        util.move_field_to_module(cr, "res.company", "stock_move_sms_validation", "stock_sms", "stock")
        util.rename_field(cr, "res.company", "stock_move_sms_validation", "stock_text_confirmation")

    util.rename_model(cr, "stock.quant.package", "stock.package")
    util.rename_xmlid(cr, "stock.view_quant_package_kanban", "stock.stock_package_view_kanban")
    util.rename_xmlid(cr, "stock.view_quant_package_tree", "stock.stock_package_view_list")
    util.rename_xmlid(cr, "stock.view_quant_package_form", "stock.stock_package_view_form")
    util.rename_xmlid(cr, "stock.quant_package_search_view", "stock.stock_package_view_search")
    util.rename_xmlid(cr, "stock.seq_quant_package", "stock.seq_package")
    util.rename_xmlid(cr, "stock.stock_quant_package_comp_rule", "stock.stock_package_comp_rule")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_all", "stock.access_stock_package_all")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_stock_manager", "stock.access_stock_package_stock_manager")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_stock_user", "stock.access_stock_package_stock_user")
    util.rename_xmlid(cr, "stock.action_report_quant_package_barcode", "stock.action_report_package_barcode")
    util.rename_xmlid(
        cr, "stock.action_report_quant_package_barcode_small", "stock.action_report_package_barcode_small"
    )
    cr.execute("UPDATE ir_sequence SET code = 'stock.package' WHERE code = 'stock.quant.package'")

    util.create_column(cr, "stock_package_type", "package_use", "varchar", default="disposable")
    cr.execute("""
        WITH reusable_types AS (
                     SELECT sp.package_type_id AS type_id
                       FROM stock_package sp
                      WHERE sp.package_type_id IS NOT NULL
                        AND sp.package_use = 'reusable'
                   GROUP BY sp.package_type_id
        )
        UPDATE stock_package_type spt
           SET package_use = 'reusable'
          FROM reusable_types rt
         WHERE spt.id = rt.type_id
    """)
    util.remove_field(cr, "stock.move", "picking_type_entire_packs")
    util.remove_field(cr, "stock.move.line", "picking_type_entire_packs")
    util.remove_field(cr, "stock.picking", "has_packages")
    util.remove_field(cr, "stock.picking", "move_line_exist")
    util.remove_field(cr, "stock.package", "package_use")

    # compute new fields
    util.create_column(cr, "stock_package", "complete_name", "varchar")
    query = """
        UPDATE stock_package sp
           SET complete_name = sp.name
    """
    util.explode_execute(cr, query, table="stock_package", alias="sp")
