from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(cr, "website_url", "local_url", only_models=("ir.attachment",))
    util.remove_field(cr, "ir.attachment", "website_url")
