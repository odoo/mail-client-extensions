from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "helpdesk.stage_cancelled", util.update_record_from_xml)
