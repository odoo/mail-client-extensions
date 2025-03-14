from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "helpdesk.ticket", "email", "partner_email")
    util.remove_field(cr, "helpdesk.ticket", "email")

    util.ensure_xmlid_match_record(
        cr,
        "helpdesk.helpdesk_team_company_rule",
        "ir.rule",
        {
            "name": "Team: multi-company",
            "model_id": util.ref(cr, "helpdesk.model_helpdesk_team"),
        },
    )
