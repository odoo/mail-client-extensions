from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "event.event_report_template_esc_label_96x134_badge")
    util.remove_record(cr, "event.action_report_event_registration_badge_96x134")
    util.change_field_selection_values(cr, "event.event", "badge_format", {"96x134": "96x82"})
