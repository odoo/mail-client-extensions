from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "property_stock_account_production_cost_id")
    util.remove_field(cr, "res.config.settings", "property_stock_account_output_categ_id")
    util.remove_field(cr, "res.config.settings", "property_stock_account_input_categ_id")
    util.remove_field(cr, "res.config.settings", "property_stock_valuation_account_id")
    util.remove_field(cr, "res.config.settings", "property_stock_journal")
    util.remove_field(cr, "res.config.settings", "group_stock_accounting_automatic")

    util.remove_field(cr, "stock.location", "valuation_out_account_id")
    util.remove_field(cr, "stock.location", "valuation_in_account_id")

    util.remove_model(cr, "stock.valuation.layer")
    util.remove_field(cr, "stock.lot", "stock_valuation_layer_ids")
    util.remove_field(cr, "account.move", "stock_valuation_layer_ids")
    util.remove_field(cr, "account.move.line", "stock_valuation_layer_ids")
    util.remove_field(cr, "stock.move", "stock_valuation_layer_ids")
    util.remove_field(cr, "product.product", "stock_valuation_layer_ids")

    util.remove_model(cr, "stock.valuation.layer.revaluation")

    util.remove_field(cr, "account.move", "stock_move_id")
    util.remove_field(cr, "stock.move", "account_move_ids")

    util.remove_field(cr, "product.product", "quantity_svl")
    util.remove_field(cr, "product.product", "value_svl")

    util.remove_field(cr, "stock.lot", "quantity_svl")
    util.remove_field(cr, "stock.lot", "value_svl")

    util.remove_field(cr, "product.category", "property_stock_account_output_categ_id")
    util.remove_field(cr, "product.category", "property_stock_account_input_categ_id")

    util.remove_view(cr, "stock_account.view_stock_quantity_history_inherit_stock_account")
    util.remove_view(cr, "stock_account.stock_valuation_layer_revaluation_form_view")
    util.remove_view(cr, "stock_account.stock_valuation_layer_picking")
    util.remove_view(cr, "stock_account.view_company_form")
    util.remove_view(cr, "stock_account.view_move_form_inherit")

    util.remove_field(cr, "stock.request.count", "accounting_date")
    util.remove_view(cr, "stock_account.stock_inventory_request_count_form_view_inherit_stock_account")

    util.change_field_selection_values(cr, "product.category", "property_valuation", {"manual_periodic": "periodic"})
