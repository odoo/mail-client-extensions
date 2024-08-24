from odoo import modules


def migrate(cr, version):
    # stay consistent with how the xml ids are dynamically generated
    # (now attached to account instead of the l10n module)
    cr.execute(
        """
        UPDATE ir_model_data
           SET module = 'account'
         WHERE model IN %s
           AND module LIKE 'l10n%%'
           AND module NOT LIKE '%%demo%%'
           AND module IN %s -- limit to standard modules
        """,
        [
            (
                "account.account",
                "account.group",
                "account.tax",
                "account.tax.repartition.line",
                # 'account.tax.group', # Those are handled in `account/saas~16.2.1.2/pre-migrate.py`
                "account.fiscal.position.tax",
                "account.fiscal.position.account",
                "account.fiscal.position",
                "account.reconcile.model",
                "account.reconcile.model.line",
            ),
            tuple(modules.get_modules()),
        ],
    )
