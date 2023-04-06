# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sign.template", "privacy")

    # copy rel for favorited users to rel for authorized users
    cr.execute("ALTER TABLE res_users_sign_template_rel RENAME TO sign_template_favorited_users_rel")
    cr.execute(
        "UPDATE ir_model_relation SET name = 'sign_template_favorited_users_rel' WHERE name = 'res_users_sign_template_rel'"
    )
    util.create_m2m(cr, "sign_template_authorized_users_rel", "res_users", "sign_template")
    cr.execute(
        """
    INSERT INTO sign_template_authorized_users_rel (res_users_id, sign_template_id)
         SELECT res_users_id, sign_template_id
           FROM sign_template_favorited_users_rel
        """
    )

    util.create_column(cr, "sign_template", "has_sign_requests", "boolean", default=False)
    cr.execute(
        """
        UPDATE sign_template st
           SET has_sign_requests = true
         WHERE EXISTS (
            SELECT id
              FROM sign_request sr
             WHERE st.id = sr.template_id
         )
        """
    )

    # upgrade security
    # update group_sign_user (name and implied_ids)
    util.update_record_from_xml(cr, "sign.group_sign_user")
    group_sign_employee_id = util.ref(cr, "sign.group_sign_employee")
    if group_sign_employee_id:
        # remove group_sign_employee
        group_sign_user_id = util.ref(cr, "sign.group_sign_user")
        util.replace_record_references_batch(
            cr, {group_sign_employee_id: group_sign_user_id}, "res.groups", replace_xmlid=False
        )
        util.remove_record(cr, "sign.group_sign_employee")

    # remove/rename old access rules
    records = [
        "sign.ir_rule_sign_template_group_sign_user",
        "sign.ir_rule_sign_template_group_sign_employee",
        "sign.ir_rule_sign_template_access_group_sign_employee",
        "sign.ir_rule_sign_template_item_access_group_sign_employee",
        "sign.ir_rule_sign_template_item_access_group_sign_user",
        "sign.ir_rule_sign_template_group_sign_manager",
        "sign.ir_rule_sign_request_group_sign_user_create",
        "sign.ir_rule_sign_request_group_sign_user_modify",
        "sign.ir_rule_sign_request_group_sign_employee_modify",
        "sign.ir_rule_sign_request_group_sign_user_modify",
        "sign.ir_rule_sign_request_group_sign_employee_modify",
        "sign.ir_rule_sign_request_group_sign_manager",
        "sign.ir_rule_sign_log_group_sign_user_modify",
        "sign.ir_rule_sign_log_group_sign_employee_modify",
        "sign.ir_rule_sign_log_group_sign_manager",
        "sign.ir_rule_sign_request_portal",
        "sign.sign_request_line_rule_portal",
        "sign.access_sign_request_all",
        "sign.access_sign_request_group_employee",
        "sign.access_sign_template_all",
        "sign.access_sign_template_group_employee",
        "sign.access_sign_request_item_all",
        "sign.access_sign_request_item_group_employee",
        "sign.access_sign_item_all",
        "sign.access_sign_item_group_employee",
        "sign.access_sign_item_option_group_employee",
        "sign.access_sign_request_item_value_all",
        "sign.access_sign_item_role_all",
        "sign.access_sign_item_role_group_employee",
        "sign.access_sign_item_type_all",
        "sign.access_sign_item_type_group_employee",
        "sign.access_sign_template_tag_employee",
        "sign.access_sign_log_all",
        "sign.access_sign_log_group_manager",
        "sign.access_sign_request_portal",
        "sign.access_sign_send_request_employee",
        "sign.access_sign_send_request_signer_employee",
    ]
    for record in records:
        util.remove_record(cr, record)

    xmlids = [
        ("sign.access_sign_template_group_user", "sign.access_sign_template_user"),
        ("sign.access_sign_request_item_group_user", "sign.access_sign_request_item_user"),
        ("sign.access_sign_item_group_user", "sign.access_sign_item_user"),
        ("sign.access_sign_item_option_group_user", "sign.access_sign_item_option_user"),
        ("sign.access_sign_request_item_value_group_user", "sign.access_sign_request_item_value_user"),
        ("sign.access_sign_item_role_group_user", "sign.access_sign_item_role_user"),
        ("sign.access_sign_item_type_group_user", "sign.access_sign_item_type_user"),
        ("sign.access_sign_send_request", "sign.access_sign_send_request_user"),
        ("sign.access_sign_send_request_signer", "sign.access_sign_send_request_signer_user"),
        ("sign.access_sign_duplicate_template_with_pdf", "sign.access_sign_duplicate_template_with_pdf_user"),
    ]
    for old_xmlid, new_xmlid in xmlids:
        util.rename_xmlid(cr, old_xmlid, new_xmlid)

    util.create_column(cr, "sign_item_role", "auth_method", "varchar")
    util.create_column(cr, "res_config_settings", "module_sign_itsme", "boolean")

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
            UPDATE sign_item_role
               SET auth_method = 'sms'
             WHERE sms_authentification = true
            """,
        ),
    )

    def auth_method_adapter(leaf, is_or, negated):
        left, operator, right = leaf
        operator = "=" if bool(right) else "!="
        return [(left, operator, "sms")]

    util.update_field_usage(
        cr, "sign.item.role", "sms_authentification", "auth_method", domain_adapter=auth_method_adapter
    )

    util.remove_field(cr, "sign.item.role", "sms_authentification")
