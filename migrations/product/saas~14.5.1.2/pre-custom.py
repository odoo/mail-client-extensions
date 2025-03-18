import logging

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade." + __name__)


def migrate(cr, version):
    # A very common custom module, "printnode_base", that's always interfering with what's done during the upgrade.
    # Existing reports are about to be removed in pre-migrate.py.
    # Their deletion should cascade onto the printnode entries referring to them.
    tables = ["printnode_report_policy", "printnode_rule", "printnode_scenario", "printnode_action_button"]
    for table in tables:
        if not util.column_exists(cr, table, "report_id"):
            continue
        cr.execute(
            f"""
            ALTER TABLE {table}
             DROP CONSTRAINT IF EXISTS {table}_report_id_fkey,
              ADD CONSTRAINT {table}_report_id_fkey
                  FOREIGN KEY (report_id) REFERENCES ir_act_report_xml(id)
                       ON DELETE CASCADE;
            """
        )
        _logger.info("Change FK of %s.report_id to be `ON DELETE CASCADE`", table)
