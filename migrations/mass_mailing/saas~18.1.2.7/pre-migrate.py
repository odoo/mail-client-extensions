from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mailing.contact", "title_id")
