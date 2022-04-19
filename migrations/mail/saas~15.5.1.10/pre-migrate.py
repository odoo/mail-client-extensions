# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.email_message_tree_view")

    util.change_field_selection_values(
        cr,
        "ir.actions.server",
        "state",
        {"email": "mail_post"},
    )
    util.create_column(cr, "ir_act_server", "mail_post_autofollow", "boolean")
    util.create_column(cr, "ir_act_server", "mail_post_method", "varchar")
    cr.execute(
        """
            UPDATE ir_act_server
               SET mail_post_method = 'email'
             WHERE state = 'mail_post'
        """
    )

    char_to_dt = """
        create function char_to_dt(text) returns timestamp as $$
        begin
            return $1::timestamp;
        exception when others then
            return NULL;
        end;
        $$ LANGUAGE plpgsql IMMUTABLE RETURNS NULL ON NULL INPUT PARALLEL SAFE;
    """
    cr.execute(char_to_dt)
    cr.execute(
        """
        ALTER TABLE mail_mail
       ALTER COLUMN scheduled_date TYPE timestamp
              USING char_to_dt(scheduled_date)
    """
    )
    cr.execute("DROP FUNCTION char_to_dt(text)")
