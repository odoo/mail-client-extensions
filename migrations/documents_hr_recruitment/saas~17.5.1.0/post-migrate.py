from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_hr_recruitment.documents_applicant_rule", force_create=False)
    util.change_field_selection_values(
        cr,
        "documents.workflow.rule",
        "create_model",
        {"hr.applicant": "hr.candidate"},
    )
