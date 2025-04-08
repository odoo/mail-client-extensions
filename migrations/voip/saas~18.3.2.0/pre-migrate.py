from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "voip.click_to_dial_field")
