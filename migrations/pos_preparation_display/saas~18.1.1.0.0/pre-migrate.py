from odoo.upgrade import util


def migrate(cr, version):
    model = "pos.prep.order" if util.version_gte("saas~18.3") else "pos_preparation_display.order"
    util.rename_field(cr, model, "pdis_general_note", "pdis_general_customer_note")
