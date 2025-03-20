from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.2"):
        util.update_record_from_xml(
            cr, "im_livechat.ir_rule_discuss_channel_member_group_im_livechat_group_manager", fields=["name"]
        )
