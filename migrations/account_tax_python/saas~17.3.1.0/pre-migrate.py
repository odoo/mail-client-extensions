from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.tax", "python_compute", "formula")
    util.remove_field(cr, "account.tax", "python_applicable")

    cr.execute(
        r"""
            UPDATE account_tax
               SET formula = REGEXP_REPLACE(
                                 REGEXP_REPLACE(formula, '\ybase_amount\y', 'base'),
                                 '^\s*result\s*=\s*',
                                 ''
                             )
             WHERE amount_type = 'code'
               AND formula IS NOT NULL
        """
    )
