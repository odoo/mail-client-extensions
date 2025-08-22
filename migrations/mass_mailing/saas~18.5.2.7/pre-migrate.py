from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mailing_mailing", "use_exclusion_list", "bool", default=True)
    util.remove_view(cr, "mass_mailing.snippet_options")
    util.remove_view(cr, "mass_mailing.snippet_options_background_options")
    util.remove_view(cr, "mass_mailing.snippet_options_border_widgets")
    util.remove_view(cr, "mass_mailing.snippet_options_border_line_widgets")
    util.remove_view(cr, "mass_mailing.s_features")
    util.remove_view(cr, "mass_mailing.s_mail_block_discount1")
