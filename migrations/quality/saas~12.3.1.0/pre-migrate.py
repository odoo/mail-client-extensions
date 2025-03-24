from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "quality_alert", "email_cc", "varchar")
    util.create_column(cr, "quality_check", "test_type_id", "integer")
    cr.execute(
        """
        UPDATE quality_check qc
           SET test_type_id = qp.test_type_id
          FROM quality_point qp
         WHERE qp.id = qc.point_id
           AND qc.test_type_id IS NULL
        """
    )
    if not util.module_installed(cr, "quality_control"):
        cr.execute("SELECT id FROM quality_point_test_type ORDER BY id LIMIT 1")
        if cr.rowcount:
            cr.execute(
                """
                UPDATE quality_check
                   SET test_type_id = %s
                 WHERE test_type_id IS NULL
                """,
                [cr.fetchone()[0]],
            )
