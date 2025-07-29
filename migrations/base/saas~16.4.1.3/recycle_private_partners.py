def recycle(env, execute=None):
    # IR.MODEL + IR.MODEL.FIELDS
    model_private_address = env.ref("base.model_x_res_partner_private", raise_if_not_found=False)
    if not model_private_address and "x_res_partner_private" not in env:
        model_private_address = env["ir.model"].create(
            {
                "name": "Private Addresses",
                "model": "x_res_partner_private",
            }
        )
        env["ir.model.fields"].create(
            {
                "name": "x_info",
                "field_description": "Personal Information",
                "ttype": "json",
                "copied": True,
                "model_id": model_private_address.id,
            }
        )
        env["ir.model.data"].create(
            {
                "name": "model_x_res_partner_private",
                "module": "base",
                "res_id": model_private_address.id,
                "model": "ir.model",
                "noupdate": True,
            }
        )
    # IR.MODEL.ACCESS
    access_private_address = env.ref("base.access_x_res_partner_private", raise_if_not_found=False)
    if not access_private_address:
        access_private_address = env["ir.model.access"].create(
            {
                "name": "Private Addresses: Admin Only",
                "model_id": model_private_address.id,
                "group_id": env.ref("base.group_system").id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
            }
        )
        env["ir.model.data"].create(
            {
                "name": "access_x_res_partner_private",
                "module": "base",
                "res_id": access_private_address.id,
                "model": "ir.model.access",
                "noupdate": True,
            }
        )
    # IR.UI.VIEW - TREE
    tree_private_address = env.ref("base.tree_x_res_partner_private", raise_if_not_found=False)
    if not tree_private_address:
        tree_private_address = env["ir.ui.view"].create(
            {
                "name": "Private Addresses Tree View",
                "model": "x_res_partner_private",
                "type": "tree",
                "arch": """
                <tree>
                    <field name="x_name"/>
                </tree>""",
            }
        )
        env["ir.model.data"].create(
            {
                "name": "tree_x_res_partner_private",
                "module": "base",
                "res_id": tree_private_address.id,
                "model": "ir.ui.view",
                "noupdate": True,
            }
        )
    # IR.UI.VIEW - FORM
    form_private_address = env.ref("base.form_x_res_partner_private", raise_if_not_found=False)
    if not form_private_address:
        form_private_address = env["ir.ui.view"].create(
            {
                "name": "Private Addresses form View",
                "model": "x_res_partner_private",
                "type": "form",
                "arch": """
                <form>
                    <group>
                        <field name="x_name"/>
                        <field name="x_info" widget="jsonb"/>
                    </group>
                </form>""",
            }
        )
        env["ir.model.data"].create(
            {
                "name": "form_x_res_partner_private",
                "module": "base",
                "res_id": form_private_address.id,
                "model": "ir.ui.view",
                "noupdate": True,
            }
        )
    # IR.ACTIONS.ACT_WINDOW
    action_private_address = env.ref("base.action_x_res_partner_private", raise_if_not_found=False)
    if not action_private_address:
        action_private_address = env["ir.actions.act_window"].create(
            {
                "name": "Private Addresses",
                "res_model": "x_res_partner_private",
                "view_mode": "tree,form",
            }
        )
        env["ir.model.data"].create(
            {
                "name": "action_x_res_partner_private",
                "module": "base",
                "res_id": action_private_address.id,
                "model": "ir.actions.act_window",
                "noupdate": True,
            }
        )
    # IR.UI.MENU
    menu_private_address = env.ref("base.menu_x_res_partner_private", raise_if_not_found=False)
    if not menu_private_address:
        menu_private_address = env["ir.ui.menu"].create(
            {
                "name": "Private Addresses",
                "action": "ir.actions.act_window," + str(action_private_address.id),
                "parent_id": env.ref("base.menu_security").id,
                "sequence": 1000,
            }
        )
        env["ir.model.data"].create(
            {
                "name": "menu_x_res_partner_private",
                "module": "base",
                "res_id": menu_private_address.id,
                "model": "ir.ui.menu",
                "noupdate": True,
            }
        )

    insert_to_x_partner_query = """
       INSERT INTO x_res_partner_private (x_name, x_info)
       SELECT p.name, jsonb_build_object(
            'Street', COALESCE(p.street, ''),
            'Street2', COALESCE(p.street2, ''),
            'City', COALESCE(p.city, ''),
            'State', COALESCE(cs.name, ''),
            'Zip', COALESCE(p.zip, ''),
            'Country', COALESCE(c.name->>'en_US', ''),
            'Phone', COALESCE(p.phone, ''),
            'Email', COALESCE(p.email, ''))
         FROM res_partner p
         JOIN res_partner_res_partner_category_rel pc
           ON pc.partner_id = p.id
    LEFT JOIN res_country c
           ON p.country_id = c.id
    LEFT JOIN res_country_state cs
           ON p.state_id = cs.id
        WHERE pc.category_id = %s
          AND COALESCE(
                p.street, p.street2, p.city, p.zip, p.phone, p.email, c.name->>'en_US', cs.name
              ) IS NOT NULL
        """
    extra_nulls = ""
    for column in [
        "email_normalized",  # mail
        "phone_sanitized",  # phone_validation
        "contact_address_complete",  # web_map
    ]:
        if column in env["res.partner"]._fields:
            extra_nulls += ", {} = NULL".format(column)

    empty_private_info_query = """
        UPDATE res_partner p
           SET
               active = false,
               type = 'contact',
               street = NULL,
               street2 = NULL,
               city = NULL,
               state_id = NULL,
               zip = NULL,
               country_id = NULL,
               phone = NULL,
               email = NULL,
               mobile = NULL
               {}
          FROM res_partner_res_partner_category_rel pc
         WHERE pc.category_id = %s
           AND pc.partner_id = p.id
        """.format(extra_nulls)

    delete_mail_messages_query = """
        DELETE FROM mail_message m
              USING res_partner_res_partner_category_rel pc
              WHERE m.model = 'res.partner'
                AND m.res_id = pc.partner_id
                AND pc.category_id = %s
        """

    # Convert/Archive private addresses + make public + empty private information / empty chatter
    tag_id = env.ref("base.res_partner_category_old_private_address").id

    if execute is None:
        execute = env.cr.execute

    execute(insert_to_x_partner_query, [tag_id])
    execute(empty_private_info_query, [tag_id])
    execute(delete_mail_messages_query, [tag_id])
