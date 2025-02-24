from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "ir.ui.menu", "web_invisible")
    util.remove_field(cr, "ir.actions.actions", "binding_invisible")
    # explicit removal for databases without odoo/odoo#199109
    util.remove_field(cr, "ir.cron", "binding_invisible")
