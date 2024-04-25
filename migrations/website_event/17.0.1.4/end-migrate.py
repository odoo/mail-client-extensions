from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT 1
          FROM ir_ui_view
         WHERE key LIKE 'website\_event.%'
           AND website_id IS NOT NULL
         FETCH FIRST ROW ONLY
        """
    )
    if cr.rowcount:
        util.add_to_migration_reports(
            """
                In Odoo 17, there was a significant overhaul of the websites
                related to displaying information about events. Please
                carefully check that your websites render correctly.
            """,
            category="Website",
        )
