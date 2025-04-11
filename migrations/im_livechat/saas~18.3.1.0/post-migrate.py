from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr, "im_livechat.ir_rule_discuss_channel_im_livechat_group_user", fields=["name", "groups"]
    )
    util.update_record_from_xml(
        cr, "im_livechat.ir_rule_discuss_channel_member_im_livechat_group_user", fields=["name", "groups"]
    )

    # These actions are removed but can be replaced by equivalent ones that already exist.
    model_rename_mapping = {
        "ir.actions.act_window": {
            "rating_rating_action_livechat_report": "im_livechat_report_channel_action",
            "rating_rating_action_livechat": "discuss_channel_action",
        },
        "ir.actions.act_window.view": {
            "rating_rating_action_livechat_view_form": "discuss_channel_action_livechat_form",
            "rating_rating_action_livechat_view_kanban": "discuss_channel_action_livechat_kanban",
            "rating_rating_action_livechat_view_tree": "discuss_channel_action_livechat_tree",
        },
    }
    for model_name, rename_mapping in model_rename_mapping.items():
        id_mapping = {}
        for old_xml_id, new_xml_id in rename_mapping.items():
            if old_ref := util.ref(cr, f"im_livechat.{old_xml_id}"):
                id_mapping[old_ref] = util.ref(cr, f"im_livechat.{new_xml_id}")
        util.replace_record_references_batch(cr, id_mapping, model_name)
        util.remove_records(cr, model_name, list(id_mapping.keys()))

    # These actions have no equivalent ones, and views target a different model.
    xml_ids_to_remove = [
        "rating_rating_action_livechat_report_view_form",
        "rating_rating_action_livechat_report_view_kanban",
        "rating_rating_menu_livechat",
        "rating_rating_view_kanban",
        "rating_rating_view_search_livechat",
        "rating_rating_view_tree",
    ]
    for xml_id in xml_ids_to_remove:
        util.remove_record(cr, f"im_livechat.{xml_id}")
