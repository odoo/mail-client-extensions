from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides_survey.slide_channel_view_kanban")
