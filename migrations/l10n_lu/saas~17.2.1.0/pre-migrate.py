def migrate(cr, version):
    # if `l10n_lu_reports` was installed before, the loading of
    # account.account.tag will crash with `UniqueViolation` because
    # it will try to recreate account.account.tag that existed before
    # => move the xmlid instead
    # Related: https://github.com/odoo/odoo/commit/8622538731d0
    # Related: https://github.com/odoo/enterprise/commit/101711858797
    cr.execute("""
        UPDATE ir_model_data
           SET module = 'l10n_lu'
         WHERE module = 'l10n_lu_reports'
           AND model = 'account.account.tag'
    """)
