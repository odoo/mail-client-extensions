from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    team_id = None
    alias_id = util.ensure_xmlid_match_record(
        cr,
        "helpdesk.helpdesk_team1_mail_alias",
        "mail.alias",
        {
            "alias_name": "support",
            "alias_parent_model_id": util.ref(cr, "helpdesk.model_helpdesk_team"),
        },
    )
    if alias_id:
        team_id = util.ensure_xmlid_match_record(cr, "helpdesk.helpdesk_team1", "helpdesk.team", {"alias_id": alias_id})
    if not team_id:
        cr.execute("SELECT id, alias_id FROM helpdesk_team ORDER BY id LIMIT 1")
        if cr.rowcount:
            team_id, alias_id = cr.fetchone()
            util.ensure_xmlid_match_record(cr, "helpdesk.helpdesk_team1", "helpdesk.team", {"id": team_id})
            util.force_noupdate(cr, "helpdesk.helpdesk_team1")
            if alias_id:
                util.ensure_xmlid_match_record(cr, "helpdesk.helpdesk_team1_mail_alias", "mail.alias", {"id": alias_id})
                util.force_noupdate(cr, "helpdesk.helpdesk_team1_mail_alias")
