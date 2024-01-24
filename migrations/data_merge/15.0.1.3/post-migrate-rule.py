from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "data_merge.data_merge_record_multi_company", util.update_record_from_xml)
