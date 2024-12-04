from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.booth", "sponsor_mobile")
