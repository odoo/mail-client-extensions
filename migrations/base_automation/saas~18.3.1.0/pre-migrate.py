from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "base.automation", "least_delay_msg")
