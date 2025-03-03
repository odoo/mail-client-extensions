from odoo.upgrade.util import remove_field


def migrate(cr, version):
    remove_field(cr, "res.config.settings", "module_website_event_meet")
