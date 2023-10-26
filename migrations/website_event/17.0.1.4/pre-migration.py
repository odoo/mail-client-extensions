from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.fold_register_details")
