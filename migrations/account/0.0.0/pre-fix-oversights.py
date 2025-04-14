from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~16.1", "saas~18.3") and util.column_exists(cr, "account_move_line", "account_type"):
        cr.execute(
            """
            SELECT 1
              FROM ir_model_fields
             WHERE model = 'account.move.line'
               AND name = 'account_type'
               AND store IS NOT TRUE
            """
        )
        if cr.rowcount:
            util.remove_column(cr, "account_move_line", "account_type")
