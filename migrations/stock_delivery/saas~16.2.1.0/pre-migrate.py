from odoo.upgrade import util


def migrate(cr, version):
    for field in ["sale_price", "destination_country_code", "carrier_id"]:
        util.move_field_to_module(cr, "stock.move.line", field, "delivery", "stock_delivery")
    if not util.column_exists(cr, "stock_move_line", "carrier_id"):
        # In case delivery was force installed in base/saas~16.2.1.3/pre-10-modules.py
        # the script in delivery/saas~16.1.1.0/pre-migrate.py won't run
        # thus we need to create the column, we cannot fill it here because we need
        # the value from stock.picking field that is yet to be created
        util.create_column(cr, "stock_move_line", "carrier_id", "int4")
        util.ENVIRON["stock_delivery_create_column"] = 1
