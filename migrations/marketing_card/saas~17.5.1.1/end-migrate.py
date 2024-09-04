from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    # fetch an actually valid record when possible (almost always is)
    cr.execute("SELECT id, user_id, res_model FROM card_campaign WHERE preview_record_ref like '%,0'")
    for campaign_id, user_id, res_model in cr.fetchall():
        res_id = env[res_model].with_user(user_id).search([], limit=1).id
        if res_id:
            cr.execute(
                """
                UPDATE card_campaign
                SET preview_record_ref = %(ref)s
                WHERE id = %(campaign_id)s
            """,
                {"campaign_id": campaign_id, "ref": f"{res_model},{res_id}"},
            )
