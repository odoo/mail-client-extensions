from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "base.module_category_services_helpdesk")
