from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "repair.view_repair_warn_uncomplete_move")
    util.remove_model(cr, "repair.warn.uncomplete.move")
