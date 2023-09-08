from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr.departure_fired")
    util.update_record_from_xml(cr, "hr.departure_resigned")
    util.update_record_from_xml(cr, "hr.departure_retired")
