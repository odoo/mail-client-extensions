from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "portal.portal_my_details_fields")
    util.remove_view(cr, "portal.portal_my_details")
