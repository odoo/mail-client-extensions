from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


UPDATED_ACCOUNTS = {
    "generic_coa": (["tax_receivable"], ["tax_payable"]),
    "ae": (["uae_account_100103"], ["uae_account_202003"]),
    "ar_base": ([], ["base_default_vat"]),
    "ar_ri": (["ri_iva_saldo_tecnico_favor"], ["ri_iva_saldo_a_pagar"]),
    "at": ([], ["chart_at_template_3530"]),
    "au": ([], ["au_21320"]),
    "bd": (["l10n_bd_200903"], ["l10n_bd_200904"]),
    "be": (["a4112"], ["a4512"]),
    "bg": (["l10n_bg_4538"], ["l10n_bg_4539"]),
    "bh": (["bh_account_200903"], ["bh_account_200904"]),
    "bo": (["l10n_bo_1142"], ["l10n_bo_21399"]),
    "br": (["account_template_102010802"], ["account_template_202011003"]),
    "ch": (["ch_coa_1176"], ["ch_coa_2201"]),
    "cl": ([], ["account_210760"]),
    "cy": ([], ["cy_2200"]),
    "cz": (["chart_cz_343001"], ["chart_cz_343002"]),
    "de_skr03": (["account_1545"], ["account_1797"]),
    "de_skr04": (["chart_skr04_1421"], ["chart_skr04_3860"]),
    "dk": (["dk_coa_6320"], ["dk_coa_7840"]),
    "ec": (
        ["ec_vat_tax_credit", "ec_withhold_tax_credit", "ec_profit_tax_credit", "ec_others_tax_credit"],
        [
            "ec_irbpnr_tax_deduction",
            "ec_vat_tax_deduction",
            "ec_ice_tax_deduction",
            "ec_profit_tax_deduction",
            "ec_others_tax_deduction",
        ],
    ),
    "ee": ([], ["l10n_ee_201200"]),
    "eg": (["egy_account_100103"], ["egy_account_202003"]),
    "es_common": (["account_common_4700"], ["account_common_4750"]),
    "fi": (["account_1764"], ["account_2939"]),
    "fr": (["pcg_44567"], ["pcg_44551"]),
    "gr": ([], ["l10n_gr_54_02_03"]),
    "hu": ([], ["l10n_hu_468"]),
    "ie": (["l10n_ie_account_2131"], ["l10n_ie_account_3804"]),
    "in": (["p10059"], ["p11239"]),
    "iq": (["iq_account_200906", "iq_account_200903"], ["iq_account_200905", "iq_account_200904"]),
    "it": ([], ["2605", "2607", "2609", "2610", "2611"]),
    "jo_standard": (["jo_account_200906"], ["jo_account_200905"]),
    "ke": (["ke1111"], ["ke2201", "ke2106"]),
    "kr": ([], ["l10n_kr_213001"]),
    "kz": (["kz1400"], ["kz3100"]),
    "lb": (["lb_account_442201"], ["lb_account_442001"]),
    "lu": (["lu_2011_account_421612"], ["lu_2011_account_461412"]),
    "ma": (["pcg_3456"], ["pcg_4456"]),
    "mn": (["account_template_1204_9902"], ["account_template_3401_9902"]),
    "mt": (["mt_2206"], ["mt_3207"]),
    "mu": (["mu_tax_receivable"], ["mu_tax_payable"]),
    "mz": (["l10n_mz_account_4438"], ["l10n_mz_account_4437"]),
    "ng": ([], ["l10n_ng_withholding_payable"]),
    "nl": ([], ["vat_tax_liabilities"]),
    "no": ([], ["chart2740"]),
    "nz": ([], ["nz_21320"]),
    "om": (["om_account_200903"], ["om_account_200904"]),
    "pk": (["l10n_pk_1123004"], ["l10n_pk_2221005"]),
    "pl": ([], ["chart22000100"]),
    "pt": (["chart_2437"], ["chart_2436"]),
    "ro": (["pcg_4424"], ["pcg_44231"]),
    "rs": (["rs_279"], ["rs_479"]),
    "rw": (["rw_108"], ["rw_308"]),
    "sa": (["sa_account_100103"], ["sa_account_202003"]),
    "se": (["a1650"], ["a2650"]),
    "sg": (["account_account_857"], ["account_account_764"]),
    "si": (["gd_acc_160800"], ["gd_acc_260800"]),
    "tr": (["tr193"], ["tr360"]),
    "tz": (["tz_108"], ["tz_308"]),
    "ug": (["3529"], ["411723"]),
    "uk": ([], ["2202", "220201"]),
    "zm": (["zm_account_8310000"], ["zm_account_9520000"]),
    "syscohada": (["pcg_4445"], ["pcg_4441"]),
    "syscebnl": ([], ["syscebnl_444"]),
}
SYSCOHADA_COA = ["bf", "bj", "cd", "cf", "cg", "ci", "cm", "ga", "gn", "gq", "gw", "km", "ml", "ne", "sn", "td", "tg"]
SYSCEBNL_COA = [
    "bf_syscebnl",
    "bj_syscebnl",
    "cd_syscebnl",
    "cf_syscebnl",
    "cg_syscebnl",
    "ci_syscebnl",
    "cm_syscebnl",
    "ga_syscebnl",
    "gn_syscebnl",
    "gq_syscebnl",
    "gw_syscebnl",
    "km_syscebnl",
    "ml_syscebnl",
    "ne_syscebnl",
    "sn_syscebnl",
    "td_syscebnl",
    "tg_syscebnl",
]

if util.version_between("18.0", "19.0"):
    from odoo import models

    from odoo.addons.account.models import account_tax  # noqa

    class AccountTaxGroup(models.Model):
        _name = "account.tax.group"
        _inherit = ["account.tax.group"]
        _module = "account"

        def write(self, vals):
            company = self.company_id
            coa = company.chart_template
            coa = "es_common" if coa.startswith("es_") else coa
            coa = "syscohada" if coa in SYSCOHADA_COA else "syscebnl" if coa in SYSCEBNL_COA else coa
            accounts = [vals[k] for k in ("tax_receivable_account_id", "tax_payable_account_id") if vals.get(k)]
            if accounts:
                accounts = self.env["account.account"].browse(accounts)
                for account in accounts:
                    if not (
                        account.account_type in ("asset_receivable", "liability_payable")
                        and account.reconcile
                        and account.non_trade
                    ):
                        xmlid = account.get_external_id().get(account.id, None)
                        if xmlid:
                            related_template = xmlid.replace("account.{}_".format(company.id), "")
                            coa_receivable, coa_payable = UPDATED_ACCOUNTS.get(coa, ([], []))
                            new_type = (
                                "asset_receivable"
                                if related_template in coa_receivable
                                else "liability_payable"
                                if related_template in coa_payable
                                else None
                            )
                            if new_type:
                                account.account_type = new_type
                                account.reconcile = True
                                account.non_trade = True
                                util.add_to_migration_reports(
                                    """
                                    <span>
                                    The account {} for company '{}' is used as a Tax Payable or a Tax Receivable account,
                                    on one or more tax groups. The account type is updated accordingly and the
                                    'Allow Reconciliation' and 'Non Trade' options are enabled.
                                    </span>
                                    """.format(
                                        util.get_anchor_link_to_record("account.account", account.id, account.name),
                                        util.html_escape(company.name),
                                    ),
                                    category="Accounting",
                                    format="html",
                                )
                                continue
                        util._logger.critical(
                            "The account %s is used as tax_receivable_account_id or tax_payable_account_id in a tax group instead of the "
                            "default account. The account does not have the correct 'type' or the 'reconcile' and 'non_trade' options.",
                            account.id,
                        )
            return super().write(vals)
