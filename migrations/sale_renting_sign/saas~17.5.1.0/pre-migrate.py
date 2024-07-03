from odoo.upgrade import util


def migrate(cr, version):
    query = (
        "UPDATE sign_request SET reference_doc = concat('sale.order,', sale_order_id) WHERE sale_order_id IS NOT NULL"
    )
    util.explode_execute(cr, query, table="sign_request")
    util.remove_field(cr, "sign.request", "sale_order_id")
    util.remove_view(cr, "sale_renting_sign.message_signature_link")
