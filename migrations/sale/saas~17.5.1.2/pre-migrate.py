from odoo.upgrade import util


def migrate(cr, version):
    subtype_to_update = [
        "mt_salesteam_order_confirmed",
        "mt_salesteam_invoice_created",
        "mt_salesteam_invoice_confirmed",
    ]

    for sub_type in subtype_to_update:
        util.if_unchanged(cr, f"sale.{sub_type}", util.update_record_from_xml)

    util.remove_field(cr, "sale.order", "analytic_account_id")
    util.remove_field(cr, "sale.report", "analytic_account_id")
    util.remove_column(cr, "sale_order", "amount_to_invoice")
    util.move_field_to_module(cr, "sale.order.line", "qty_invoiced_posted", "l10n_it_edi_doi", "sale")
    util.remove_column(cr, "sale_order_line", "qty_invoiced_posted")
