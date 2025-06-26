from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "website_slides.course_card_information_arrow", "website_slides.course_card_information_badge"
    )
