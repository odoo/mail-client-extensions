from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "portal.portal_record_layout")
