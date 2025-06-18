from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_between("16.0", "19.0"):
        return
    cr.execute("""
        DELETE FROM ir_sequence_date_range
        WHERE id NOT IN (
              SELECT MIN(id)
                FROM ir_sequence_date_range
            GROUP BY sequence_id, date_from, date_to
        )
    """)
