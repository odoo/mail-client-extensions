from odoo.upgrade import util


def migrate(cr, version):
    subtype_to_update = [
        "mt_salesteam_order_confirmed",
        "mt_salesteam_invoice_created",
        "mt_salesteam_invoice_confirmed",
    ]

    for sub_type in subtype_to_update:
        util.if_unchanged(cr, f"sale.{sub_type}", util.update_record_from_xml)
