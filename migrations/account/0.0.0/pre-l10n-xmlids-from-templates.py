# -*- coding: utf-8 -*-


def migrate(cr, version):
    # accounts, taxes, fiscal positions, ... created from chart templates are all be set to noupdate True
    # Actually, there isn't any data file adding directly an `account.account` or an `account.tax` itself,
    # they are all supposed to be generated from templates. We can therefore assume all accounts, taxes, ...
    # can be automatically set to noupdate True, in case the user somehow reset them to noupdate False.
    # Otherwise, they get deleted at the end of the upgrade, and if they are referenced, it raises.
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = 't'
         WHERE module like 'l10n_%'
           AND model in (
                'account.account',
                'account.tax',
                'account.fiscal.position',
                'account.fiscal.position.account',
                'account.fiscal.position.tax'
             )
    """)
