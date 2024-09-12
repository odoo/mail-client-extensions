from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "pos_order", "blackbox_pos_receipt_time")
    util.remove_field(cr, "pos.session", "total_base_of_measure_tax_a")
    util.remove_field(cr, "pos.session", "total_base_of_measure_tax_b")
    util.remove_field(cr, "pos.session", "total_base_of_measure_tax_c")
    util.remove_field(cr, "pos.session", "total_base_of_measure_tax_d")
    util.remove_record(cr, "pos_blackbox_be.sale_report_sequenceX")
    util.remove_record(cr, "pos_blackbox_be.sale_report_sequenceZ")
