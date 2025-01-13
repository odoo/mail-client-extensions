from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "base.paperformat_euro", util.update_record_from_xml)
    util.if_unchanged(cr, "base.paperformat_us", util.update_record_from_xml)
