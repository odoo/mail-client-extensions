from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "ir.attachment", "website_url", "local_url")
    util.remove_field(cr, "ir.attachment", "website_url")
