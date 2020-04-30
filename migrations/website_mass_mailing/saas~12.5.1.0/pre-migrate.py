# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        CREATE TABLE website_mass_mailing_popup (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            mailing_list_id int4,
            website_id int4,
            popup_content text
        )
    """
    )
    cr.execute(
        """
        INSERT INTO website_mass_mailing_popup(mailing_list_id, popup_content)
             SELECT id, popup_content
               FROM mailing_list
    """
    )

    util.remove_field(cr, "mailing.list", "popup_content")
    util.remove_field(cr, "mailing.list", "popup_redirect_url")
    util.remove_field(cr, "res.config.settings", "group_website_popup_on_exit")

    util.remove_record(cr, "website_mass_mailing.group_website_popup_on_exit")
    util.remove_view(cr, "website_mass_mailing.view_mail_mass_mailing_list_form")
    util.remove_view(cr, "website_mass_mailing.res_config_settings_view_form")
