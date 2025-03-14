from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_website_event_questions")
    util.create_column(cr, "event_registration", "company_name", "varchar")
