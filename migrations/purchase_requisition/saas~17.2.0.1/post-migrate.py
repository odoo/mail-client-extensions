from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    user_group = env.ref("base.group_user")
    purchase_group = env.ref("purchase_requisition.group_purchase_alternatives")
    user_group._apply_group(purchase_group)
