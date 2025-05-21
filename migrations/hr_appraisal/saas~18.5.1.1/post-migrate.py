from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_confirm", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.hr_appraisal_default_template", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_request_from_employee", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.hr_appraisal_note_comp_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_reminder", util.update_record_from_xml)
