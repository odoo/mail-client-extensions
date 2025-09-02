from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~16.2", "18.0"):
        util.create_column(cr, "hr_expense_sheet", "approval_state", "varchar")
        util.explode_execute(
            cr,
            """
                UPDATE hr_expense_sheet sheet
                   SET approval_state = CASE
                           WHEN state IN ('approve', 'post', 'done') THEN 'approve'
                           WHEN state = 'cancel' THEN 'cancel'
                           ELSE 'submit'
                       END
                WHERE sheet.approval_state IS NULL AND sheet.state != 'draft'
            """,
            "hr_expense_sheet",
            alias="sheet",
        )
