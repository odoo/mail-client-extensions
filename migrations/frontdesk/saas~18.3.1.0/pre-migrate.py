from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "frontdesk.frontdesk", "mail_template_id")
