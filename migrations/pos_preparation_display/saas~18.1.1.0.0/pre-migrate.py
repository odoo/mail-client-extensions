from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos_preparation_display.order", "pdis_general_note", "pdis_general_customer_note")
