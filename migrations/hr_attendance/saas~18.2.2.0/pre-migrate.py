from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DELETE FROM hr_attendance_overtime WHERE date IS NULL")
    amount_deleted = cr.rowcount

    # warn admins
    if amount_deleted:
        util.add_to_migration_reports(
            f"""
<details>
<summary>
    {amount_deleted} overtime records were deleted from your database because
    they did not have a date and overtime records are now required to be dated.
</summary>
</details>
            """,
            category="Overtime",
            format="html",
        )
