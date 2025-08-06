from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mailing_mailing", "use_exclusion_list", "bool", default=True)
