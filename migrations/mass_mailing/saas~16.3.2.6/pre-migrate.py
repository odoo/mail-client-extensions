from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.snippet_options_extra_shapes")
    util.remove_view(cr, "mass_mailing.snippet_options_image_styles")
