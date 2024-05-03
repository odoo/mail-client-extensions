from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_appraisal.hr_appraisal_all_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.hr_appraisal_emp_rule", util.update_record_from_xml)
