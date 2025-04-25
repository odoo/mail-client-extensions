from odoo.upgrade import util


def migrate(cr, version):
    # Catching missing renames from wrong script from saas~17.5
    util.rename_xmlid(
        cr,
        "documents_hr_recruitment.documents_recruitment_plans_tag",
        "documents_hr_recruitment.documents_tag_recruitment_reserve",
        on_collision="merge",
    )
    util.rename_xmlid(
        cr,
        "documents_hr_recruitment.documents_recruitment_sheet_tag",
        "documents_hr_recruitment.documents_tag_cancelled",
        on_collision="merge",
    )
