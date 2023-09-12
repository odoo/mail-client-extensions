# -*- coding: utf-8 -*-
import json

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.tax", "l10n_mx_tax_type", "l10n_mx_factor_type")
    # init the tax type for all mexican taxes, use the tax group's xmlid if possible
    util.create_column(cr, "account_tax", "l10n_mx_tax_type", "varchar")

    group_to_val = {}
    cr.execute("SELECT id FROM res_company")
    for (cid,) in cr.fetchall():
        group_to_val[util.ref(cr, f"account.{cid}_tax_group_isr_ret_10")] = "isr"
        for ieps_rate in ("8", "25", "26_5", "30", "53"):
            group_to_val[util.ref(cr, f"account.{cid}_tax_group_ieps_{ieps_rate}")] = "ieps"

    if None in group_to_val:
        del group_to_val[None]  # in case one of the groups had a removed xmlid

    group_to_val = json.dumps(group_to_val)
    queries = [
        cr.mogrify(query, [group_to_val])
        for query in util.explode_query_range(
            cr,
            """
            UPDATE account_tax t
               SET l10n_mx_tax_type = COALESCE((%s::jsonb)->>t.tax_group_id::text, 'iva')
              FROM res_country rc
             WHERE rc.id = t.country_id
               AND rc.code = 'MX'
            """,
            table="account_tax",
            alias="t",
        )
    ]
    util.parallel_execute(cr, queries)
