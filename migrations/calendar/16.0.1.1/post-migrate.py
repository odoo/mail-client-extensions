from odoo.upgrade import util


def migrate(cr, version):
    for template_id_suffix in ["invitation", "changedate", "reminder", "update"]:
        util.if_unchanged(cr, f"calendar.calendar_template_meeting_{template_id_suffix}", util.update_record_from_xml)
