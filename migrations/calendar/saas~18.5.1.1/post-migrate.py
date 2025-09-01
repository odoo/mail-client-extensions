from odoo.upgrade import util


def migrate(cr, version):
    for template in ["meeting_invitation", "meeting_changedate", "meeting_reminder", "meeting_update", "delete_event"]:
        util.if_unchanged(cr, f"calendar.calendar_template_{template}", util.update_record_from_xml)
