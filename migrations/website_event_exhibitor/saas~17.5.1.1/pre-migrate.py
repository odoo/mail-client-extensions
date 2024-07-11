from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_event_exhibitor.event_report_template_full_page_ticket_inherit_exhibitor")
