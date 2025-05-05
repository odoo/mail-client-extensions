from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~17.2", "saas~18.3"):
        # update values for DBs that already upgraded and have wrong method type
        util.create_column(cr, "pos_payment_method", "payment_method_type", "varchar", default="none")
        cr.execute(
            """
                UPDATE pos_payment_method
                   SET payment_method_type = 'terminal'
                 WHERE payment_method_type = 'none'
                   AND use_payment_terminal IS NOT NULL
            """
        )
