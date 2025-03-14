from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "onboarding.onboarding", "panel_background_color")
    util.remove_field(cr, "onboarding.onboarding", "panel_background_image")
