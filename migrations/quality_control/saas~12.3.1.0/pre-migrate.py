from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "quality_control.test_type_passfail")
    cr.execute(
        """
        UPDATE quality_check
           SET test_type_id = %s
         WHERE test_type_id IS NULL
        """,
        [util.ref(cr, "quality_control.test_type_passfail")],
    )
