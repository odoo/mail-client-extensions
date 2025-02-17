from odoo.upgrade import util


def migrate(cr, version):
    # create column to avoid computation of new field whose value will always be False
    util.create_column(cr, "discuss_channel", "has_crm_lead", "boolean")
