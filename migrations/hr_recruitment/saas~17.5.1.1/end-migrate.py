from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "hr_recruitment.refuse_reason_3", "hr_recruitment.refuse_reason_4")
    for num in [1, 2, 5, 6, 7, 8]:
        util.if_unchanged(cr, f"hr_recruitment.refuse_reason_{num}", util.update_record_from_xml)

    util.update_record_from_xml(cr, "hr_recruitment.mt_job_new")
    util.update_record_from_xml(cr, "hr_recruitment.mt_department_new")

    util.remove_view(cr, "hr_recruitment.hr_recruitment_source_kanban")
