from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "board.menu_board_my_dash", noupdate=False)
