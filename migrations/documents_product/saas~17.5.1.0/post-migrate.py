from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_product.ir_actions_server_create_product_template")
