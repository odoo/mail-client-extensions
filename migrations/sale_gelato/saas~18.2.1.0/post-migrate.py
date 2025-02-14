from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_gelato.order_status_update", util.update_record_from_xml)
