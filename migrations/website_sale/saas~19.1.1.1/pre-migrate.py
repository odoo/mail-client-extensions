from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "website", "enabled_gmc_src")
