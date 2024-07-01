from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "event.event_stage_booked", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_stage_done", util.update_record_from_xml)
