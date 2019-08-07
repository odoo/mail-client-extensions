# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'tax_accounts_v12_bckp'):
        return

    cr.execute("savepoint l10n_in_inject_financial_report;")

    #If a tax is type_tax_use 'none', we artifically switch it to its parent type temporarily, to check what grids to impact for it
    cr.execute("""
        update account_tax
        set type_tax_use = parent.type_tax_use, name = concat(account_tax.name, account_tax.id::varchar)
        from account_tax_filiation_rel tx_rel, account_tax parent
        where tx_rel.child_tax = account_tax.id
        and parent.id = tx_rel.parent_tax
        and account_tax.type_tax_use = 'none';
    """) #Groups with type_tax_use = 'none' are not supported, so no group of group here

    cr.execute("""
       select max(id)
       from financial_report_lines_v12_bckp
    """)
    next_financial_rep_ln_id = cr.fetchall()[0][0] + 1

    query_params = []

    # These tags have been converted to tax report lines in 12.3, but did not correspond
    # to any financial report line
    tags_to_treat = [('SGST', 'sgst_tag_tax'), ('CGST', 'cgst_tag_tax'), ('IGST', 'igst_tag_tax'), ('CESS', 'cess_tag_tax')]

    for (tag_name, xmlid) in tags_to_treat:
        for tax_type in ('sale', 'purchase'):
            cr.execute("""
                select distinct account_account_tag_id
                from account_tax_account_tag_v12_bckp
                join account_tax
                on account_tax.id = account_tax_account_tag_v12_bckp.account_tax_id
                where module = 'l10n_in'
                and xmlid = %(xmlid)s
                and account_tax.type_tax_use = %(tax_type)s
            """, {
                'xmlid': xmlid,
                'tax_type': tax_type,
            })

            rslt = cr.fetchall()
            if rslt:
                tag_id = rslt[0][0]

                if tag_name in ('IGST', 'CGST', 'SGST'):
                    sign = tax_type == 'sale' and '-' or ''
                else:
                    sign = tax_type == 'purchase' and '-' or ''

                query_params.append({
                    'id': next_financial_rep_ln_id,
                    'xmlid': 'fake_l10n_in_line_' + tax_type + '_'  + xmlid,
                    'name': tag_name,
                    'domain': "[('tax_line_id.tag_ids', '=', %s), ('tax_line_id.type_tax_use', '=', '%s')]" % (str(tag_id), tax_type),
                    'formulas': 'balance = %ssum.balance' % (sign),
                })

                next_financial_rep_ln_id += 1

    # Some tax groups have been converted to tax report lines
    for (group_name, tag_name) in [('exempt_group', 'Exempt'), ('nil_rated_group', 'Nil Rated')]:
        for tax_type in ('sale', 'purchase'):
            cr.execute("""
                select account_tax.id
                from account_tax
                join ir_model_data
                on ir_model_data.res_id = account_tax.tax_group_id
                   and ir_model_data.model = 'account.tax.group'
                   and ir_model_data.name = %(group_name)s
                where
                account_tax.type_tax_use = %(tax_type)s;
            """, {'group_name': group_name, 'tax_type': tax_type})

            tax_ids = [tax_id for (tax_id,) in cr.fetchall()]

            # We use a fake tag id equal to 0, so that we're sure it isn't used by other tags or report lines
            query_params.append({
                'id': next_financial_rep_ln_id,
                'xmlid': 'fake_l10n_in_line_tax_group_' + group_name + '_' + tax_type,
                'name': tag_name,
                'domain': "[('tax_ids', 'in', %s), ('tax_ids.tag_ids', '=', 0)]" % (str(tax_ids)),
                'formulas': 'balance = %ssum.balance' % (tax_type == 'purchase' and '-' or ''),
            })

            next_financial_rep_ln_id += 1

    cr.execute("rollback to savepoint l10n_in_inject_financial_report;")

    # We inject our fake tag on every indian tax we want to fix
    cr.execute("""
        insert into account_tax_account_tag_v12_bckp(account_tax_id, account_account_tag_id)
        select account_tax.id, 0
        from account_tax
        join ir_model_data
        on ir_model_data.res_id = account_tax.tax_group_id
           and ir_model_data.model = 'account.tax.group'
           and ir_model_data.name in ('exempt_group', 'nil_rated_group');
    """)

    for params in query_params:
        cr.execute("""
            insert into financial_report_lines_v12_bckp(id, xmlid, name, domain, formulas, module)
            values (%(id)s, %(xmlid)s, %(name)s, %(domain)s, %(formulas)s, 'l10n_in_reports')
        """, params)
