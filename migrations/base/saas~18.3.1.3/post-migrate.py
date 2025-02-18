from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    user = env["res.users"].browse(util.ref(cr, "base.default_user"))
    default_group_id = util.ref(cr, "base.default_user_group")
    env["res.groups"].browse(default_group_id).write(
        {
            "implied_ids": [(6, 0, (user.group_ids - user.group_ids.implied_ids.all_implied_ids).ids)],
        }
    )
