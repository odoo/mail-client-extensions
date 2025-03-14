from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides.slide_icon")
    util.remove_view(cr, "website_slides.private_profile")

    util.remove_field(cr, "slide.channel", "partner_all_ids")

    util.remove_field(cr, "res.partner", "slide_channel_all_ids", drop_column=False)
