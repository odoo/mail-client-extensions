from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    module = "l10n_lu_hr_payroll"
    xmlids = [
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_1"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1_2017"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1_2024"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1_2025"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1_2017"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1_2024"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1_2025"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_1a"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1a_2017"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1a_2024"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_1a_2025"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1a"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1a_2017"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1a_2024"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_1a_2025"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_2"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_2_2017"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_2_2024"),
        eb("rule_parameter_l10n_lu_withholding_annual_{,nonperiodic_}taxes_2_2025"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_2"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_2_2017"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_2_2024"),
        eb("rule_parameter_withholding_annual_{,nonperiodic_}taxes_threshold_2_2025"),
    ]
    for old, new in xmlids:
        util.rename_xmlid(cr, f"{module}.{old}", f"{module}.{new}")
