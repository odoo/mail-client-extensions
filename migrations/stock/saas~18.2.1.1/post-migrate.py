from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "stock.mail_template_data_delivery_confirmation", util.update_record_from_xml)
