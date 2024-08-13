from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.event", "date_begin_located")
    util.remove_field(cr, "event.event", "date_end_located")
