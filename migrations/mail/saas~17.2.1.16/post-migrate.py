from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO mail_canned_response_res_groups_rel (mail_canned_response_id, res_groups_id)
             SELECT id AS mail_canned_response_id, %s as res_groups_id
               FROM mail_canned_response
        """,
        [util.ref(cr, "base.group_user")],
    )
    base_group_system = util.env(cr).ref("base.group_system")
    base_group_system.write({"implied_ids": [(4, util.ref(cr, "mail.group_mail_canned_response_admin"))]})
