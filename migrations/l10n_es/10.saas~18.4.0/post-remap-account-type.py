# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    type_xmlids = {
        x: util.ref(cr, x)
        for x in [
            "account.data_account_type_current_liabilities",
            "account.data_account_type_current_assets",
            "l10n_es.account_type_financieras",
        ]
    }

    if all(type_xmlids.values()):
        # If all account types
        # account.data_account_type_current_liabilities
        # account.data_account_type_current_assets
        # l10n_es.account_type_financieras
        # exists in database, re-map the accounts as done in odoo/odoo@3e1d46dcc90fb09f24de49783f0f1c1d50058186
        cr.execute("""
            UPDATE account_account
               SET user_type_id = CASE
                    WHEN code ilike '50%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '51%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '52%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '53%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '54%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '550%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '552%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '554%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '555%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '556%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '557%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '5580%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '5585%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '5590%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '5595%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '560%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '561%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '565%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '566%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '567%%' THEN %(account.data_account_type_current_assets)s
                    WHEN code ilike '568%%' THEN %(account.data_account_type_current_liabilities)s
                    WHEN code ilike '59%%' THEN %(account.data_account_type_current_assets)s
                    ELSE %(l10n_es.account_type_financieras)s
               END
             WHERE user_type_id = %(l10n_es.account_type_financieras)s
        """, type_xmlids)

    type_xmlids["l10n_es.account_type_terceros"] = terceros = util.ref(cr, "l10n_es.account_type_terceros")
    if terceros and type_xmlids["account.data_account_type_current_liabilities"]:
        cr.execute("""
            UPDATE account_account
               SET user_type_id = %(account.data_account_type_current_liabilities)s
             WHERE user_type_id = %(l10n_es.account_type_terceros)s
               AND code LIKE '49%%'
        """, type_xmlids)

    for xmlid in ['l10n_es.account_type_financieras', 'l10n_es.account_type_terceros']:
        if not type_xmlids[xmlid]:
            continue
        cr.execute("""
            SELECT count(*)
              FROM account_account
             WHERE user_type_id = %s
        """, (type_xmlids[xmlid],))
        if cr.fetchone()[0]:
            # In case we were not able to re-map all accounts of type financieras/terceros, keep it.
            util.force_noupdate(cr, xmlid, True)
