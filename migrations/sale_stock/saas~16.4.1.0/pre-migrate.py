from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_stock.report_invoice_document_inherit_sale_stock")
    util.remove_view(cr, "sale_stock.res_config_settings_view_form_sale")
    util.remove_field(cr, "res.config.settings", "group_display_incoterm")
    util.remove_record(cr, "sale_stock.group_display_incoterm")

    query = """
                UPDATE account_move move
                   SET incoterm_location = so.incoterm_location
                  FROM sale_order so
                  JOIN sale_order_line sol ON sol.order_id = so.id
                  JOIN sale_order_line_invoice_rel solir ON solir.order_line_id = sol.id
                  JOIN account_move_line aml ON aml.id = solir.invoice_line_id
                 WHERE move.id = aml.move_id
                   AND so.incoterm_location IS NOT NULL
            """
    util.explode_execute(cr, query, table="account_move", alias="move")
