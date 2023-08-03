from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "worksheet.ir_rule_worksheet_template_multi_company", util.update_record_from_xml)
