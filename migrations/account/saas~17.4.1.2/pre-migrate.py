from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "send_mail_warning_message")
    util.remove_field(cr, "account.move.send", "sequence_gap_warning")
    util.rename_field(cr, "mail.message", "show_audit_log", "account_audit_log_activated")
    util.remove_field(cr, "mail.message", "account_audit_log_display_name")
    util.remove_view(cr, "account.res_config_settings_view_form_inherit_account_audit_trail")
    util.remove_view(cr, "account.view_account_payment_method_line_kanban")
    util.change_field_selection_values(
        cr,
        "account.report",
        "default_opening_date_filter",
        {
            "last_month": "previous_month",
            "last_quarter": "previous_quarter",
            "last_year": "previous_year",
            "last_tax_period": "previous_tax_period",
        },
    )
    util.force_noupdate(cr, "account.account_invoices", noupdate=False)


def update_pos_receipt_labels(cr, operator, chart_template_code):
    """
    Updates the pos_receipt_label for all tax groups in companies using the specified chart template.

    :param operator: operatod used in the search domain
    :param chart_template_code: Code of the chart template (e.g., "it")
    """
    env = util.env(cr)
    CoA = env["account.chart.template"]
    tax_group_labels = {}

    for company in env["res.company"].search([("chart_template", operator, chart_template_code)], order="parent_path"):
        tax_group_data = CoA._get_chart_template_data(company.chart_template)["account.tax.group"]
        tax_group_labels.update(
            {
                f"{company.id}_{key}": value["pos_receipt_label"]
                for key, value in tax_group_data.items()
                if "pos_receipt_label" in value
            }
        )

    if not tax_group_labels:
        return

    cr.execute(
        """
        UPDATE account_tax_group tax_group
           SET pos_receipt_label = tax_group_data.label
          FROM json_each_text(%s) AS tax_group_data(name, label)
          JOIN ir_model_data imd
            ON imd.module = 'account'
           AND imd.name = tax_group_data.name
           AND imd.model = 'account.tax.group'
         WHERE tax_group.id = imd.res_id
        """,
        [Json(tax_group_labels)],
    )
