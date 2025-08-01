from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_cost_of_sales_62")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_cost_of_sales_62_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_operating_expenses_63")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_operating_expenses_63_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_financial_expenses_66_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_financial_expenses_66_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_net_period_profit_or_loss_692")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_net_period_profit_or_loss_692_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_profit_or_loss_for_the_period_690")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_profit_or_loss_for_the_period_690_balance")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_prov_taxes_statutory_oblig_691")
    util.remove_record(cr, "l10n_tr_reports.account_report_line_tr_pl_prov_taxes_statutory_oblig_691_balance")
    cr.execute(
        """
        UPDATE account_report_line l
           SET hide_if_zero = False
          FROM ir_model_data d
         WHERE l.id =  d.res_id
           AND d.model = 'account.report.line'
           AND d.module = 'l10n_tr_reports'
           AND d.name IN (
                'account_report_line_tr_pl_sales_deductions_61',
                'account_report_line_tr_pl_non_operating_profit_lost',
                'account_report_line_tr_pl_extraordinary_revenues_profit_67',
                'account_report_line_tr_pl_extraordinary_expenses_losses_68'
            )
        """
    )
