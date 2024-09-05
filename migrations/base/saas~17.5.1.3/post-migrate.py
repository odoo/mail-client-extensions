from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "base.MVR", util.update_record_from_xml)
