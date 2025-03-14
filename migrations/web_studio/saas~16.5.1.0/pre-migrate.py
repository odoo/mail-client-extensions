from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web_studio.simplified_form_view_import_module")
