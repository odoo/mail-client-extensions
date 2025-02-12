from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sms.composer", "mass_use_blacklist", "use_exclusion_list")
