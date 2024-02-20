# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    accounting_country_codes = (
        "ae,ar,at,au,be,bg,bo,br,ca,ch,cl,cn,co,cr,cz,de,dk,do,dz,ec,ee,eg,"
        "es,et,fi,fr,gr,gt,hk,hn,hr,hu,id,ie,il,in,it,jp,ke,kz,lt,lu,lv,ma,"
        "mn,mx,my,mz,nl,no,nz,pa,pe,ph,pk,pl,pt,ro,rs,sa,se,sg,si,sk,th,tn,"
        "tr,tw,ua,ug,uk,us,uy,ve,vn,za,syscohada".split(",")
    )

    eb = util.expand_braces
    for cc in accounting_country_codes:
        util.rename_xmlid(cr, *eb(f"{{l10n_{cc},base}}.partner_demo_company_{cc}"), on_collision="merge")
        util.rename_xmlid(cr, *eb(f"{{l10n_{cc},base}}.demo_company_{cc}"), on_collision="merge")
        util.rename_xmlid(cr, *eb(f"{{l10n_{cc},base}}.demo_bank_{cc}"), on_collision="merge")

    util.rename_xmlid(
        cr, "l10n_hr_kuna.partner_demo_company_hr", "base.partner_demo_company_hr_kuna", on_collision="merge"
    )
    util.rename_xmlid(cr, "l10n_hr_kuna.demo_company_hr", "base.demo_company_hr_kuna", on_collision="merge")

    ar_specific_xmlids = [
        "company_ri",
        "company_mono",
        "company_exento",
        "partner_ri",
        "partner_mono",
        "partner_exento",
        "bank_account_ri",
    ]
    for cc in ar_specific_xmlids:
        util.rename_xmlid(cr, *eb(f"{{l10n_ar,base}}.{cc}"), on_collision="merge")

    util.rename_xmlid(cr, "l10n_ch.partner_demo_company_bank_account", "base.demo_bank_ch", on_collision="merge")

    util.rename_xmlid(cr, "l10n_dz.l10n_dz_demo_company", "base.partner_demo_company_dz", on_collision="merge")
    util.rename_xmlid(cr, "l10n_dz.l10n_dz_demo_company_company", "base.demo_company_dz", on_collision="merge")

    util.rename_xmlid(cr, "l10n_ma.l10n_ma_demo_company", "base.partner_demo_company_ma", on_collision="merge")
    util.rename_xmlid(cr, "l10n_ma.l10n_ma_demo_company_company", "base.demo_company_ma", on_collision="merge")

    util.rename_xmlid(cr, *eb("{l10n_mx_edi,base}.partner_demo_company_2_mx"), on_collision="merge")
    util.rename_xmlid(cr, *eb("{l10n_mx_edi,base}.demo_company_2_mx"), on_collision="merge")

    util.rename_xmlid(cr, *eb("{l10n_fr_account,base}.partner_demo_company_fr"), on_collision="merge")
    util.rename_xmlid(cr, *eb("{l10n_fr_account,base}.demo_company_fr"), on_collision="merge")
    util.rename_xmlid(cr, *eb("{l10n_fr_account,base}.demo_bank_fr"), on_collision="merge")

    payroll_country_codes = "ae,au,be,ch,fr,hk,in,ke,lt,lu,ma,mx,nl,pl,ro,sa,sk,us".split(",")
    for country_code in payroll_country_codes:
        util.force_noupdate(cr, f"l10n_{country_code}_hr_payroll.res_partner_company_{country_code}", noupdate=True)
        util.force_noupdate(cr, f"l10n_{country_code}_hr_payroll.res_company_{country_code}", noupdate=True)

    payroll_company_ids = [
        util.ref(cr, f"l10n_{country_code}_hr_payroll.res_company_{country_code}")
        for country_code in payroll_country_codes
    ] + [util.ref(cr, "l10n_hk_hr_payroll.demo_company_hk")]
    payroll_company_ids = [cid for cid in payroll_company_ids if cid]
    if payroll_company_ids:
        cr.execute(
            """
            UPDATE res_company company
               SET name = company.name || ' DEMO'
             WHERE id in %s
        """,
            [tuple(payroll_company_ids)],
        )
