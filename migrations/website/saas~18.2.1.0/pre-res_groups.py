from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "website.page.properties", "groups_id", "group_ids")
