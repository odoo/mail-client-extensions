from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "base_import_module.module_tree_apps_inherit")
