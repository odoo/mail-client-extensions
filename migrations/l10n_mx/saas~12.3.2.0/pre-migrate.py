# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_mx.tag_diot_16", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_16_non_cre", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_16_imp", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_0", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_8", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_8_non_cre", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_ret", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_exento", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax9", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax12", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax1", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax2", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax3", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax5", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax7", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax8", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax13", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax14", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax16", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax17", noupdate=False)

    cr.execute("""
        INSERT INTO v12_financial_tags_registry(tag_id)
        SELECT res_id
        FROM ir_model_data
        JOIN account_account_tag
        ON account_account_tag.id = ir_model_data.res_id
        WHERE ir_model_data.module = 'l10n_mx'
            AND ir_model_data.model = 'account.account.tag'
            AND account_account_tag.applicability = 'taxes';
    """)

    # Some financial tags are not used in any financial report line ; we need to inject some lines to migrate them

    cr.execute("""
        SELECT MAX(id)
        FROM financial_report_lines_v12_bckp
    """)
    next_financial_line_id = cr.fetchall()[0][0] + 1

    for rep_type, tag_xmlids in (('base', ('tag_diot_0', 'tag_diot_16', 'tag_diot_8')), ('tax', ('tag_diot_ret', 'tag_iva', 'tag_isr', 'tag_ieps'))):
        domain_prefix = rep_type == 'base' and 'tax_ids.tag_ids' or 'tax_line_id.tag_ids'

        cr.execute("""
            SELECT name, res_id
            FROM ir_model_data
            WHERE model = 'account.account.tag'
            AND module = 'l10n_mx'
            AND name in %(xmlids)s
        """, {'xmlids': tag_xmlids})

        for tag_xmlid, tag_id in cr.fetchall():

            cr.execute("""
                INSERT INTO financial_report_lines_v12_bckp(id, xmlid, name, domain, formulas, module)
                VALUES (%(id)s, %(xmlid)s, %(name)s, %(domain)s, %(formulas)s, 'l10n_mx_reports')
            """, {'id': next_financial_line_id, 'xmlid': 'MX_INJECTED_TAG_'+str(tag_id), 'name': 'Tournicoti', 'domain': str([(domain_prefix, 'in', (tag_id,))]), 'formulas': 'balance=sum.balance'})
            next_financial_line_id += 1