from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "pos_blackbox_be.sale_report_sequenceZUser")
    util.delete_unused(cr, "pos_blackbox_be.sale_report_sequenceXUser")
    util.remove_field(cr, "pos.order.line", "vat_letter")
