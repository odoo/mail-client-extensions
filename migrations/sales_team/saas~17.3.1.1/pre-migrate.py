from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sales_team.res_partner_view_team")

    query = """
        INSERT INTO mail_message (
                    res_id, model, author_id, message_type, date,
                    body
             )
             SELECT r.id, 'res.partner', %s, 'notification', NOW() at time zone 'UTC',
                    'Former Sales Team: ' || (t.name->>'en_US') || ' (id=' || r.team_id || ')'
               FROM res_partner r
               JOIN crm_team t
                 ON r.team_id = t.id
    """

    util.explode_execute(
        cr, cr.mogrify(query, [util.ref(cr, "base.partner_root")]).decode(), table="res_partner", alias="r"
    )

    util.remove_field(cr, "res.partner", "team_id")
