from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "gift_card_settings")
    util.remove_field(cr, "res.config.settings", "pos_gift_card_settings")
