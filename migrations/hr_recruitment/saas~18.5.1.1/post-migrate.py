from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment.degree_graduate", fields=["score"])
    util.update_record_from_xml(cr, "hr_recruitment.degree_bachelor", fields=["score"])
    util.update_record_from_xml(cr, "hr_recruitment.degree_licenced", fields=["score"])
    util.update_record_from_xml(cr, "hr_recruitment.degree_bac5", fields=["score"])
