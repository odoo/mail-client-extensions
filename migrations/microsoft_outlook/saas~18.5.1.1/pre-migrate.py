from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "microsoft.outlook.mixin", "is_microsoft_outlook_configured")
