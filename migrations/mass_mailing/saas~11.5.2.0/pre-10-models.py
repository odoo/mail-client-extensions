# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pk = util.get_index_on(cr, "mail_mass_mailing_contact_list_rel", "contact_id", "list_id")
    if pk and pk.ispk:
        # Primary key found, remove it.
        # The ORM will create the missing unique constraint
        pk.drop(cr)

    cr.execute("ALTER TABLE mail_mass_mailing_contact_list_rel ADD COLUMN id SERIAL NOT NULL PRIMARY KEY")
    util.create_column(cr, "mail_mass_mailing_contact_list_rel", "create_uid", "integer")
    util.create_column(cr, "mail_mass_mailing_contact_list_rel", "create_date", "timestamp without time zone")
    util.create_column(cr, "mail_mass_mailing_contact_list_rel", "write_uid", "integer")
    util.create_column(cr, "mail_mass_mailing_contact_list_rel", "write_date", "timestamp without time zone")
    util.create_column(cr, "mail_mass_mailing_contact_list_rel", "opt_out", "boolean")

    util.create_column(cr, "mail_mass_mailing_list", "is_public", "boolean")
    cr.execute("UPDATE mail_mass_mailing_list set is_public=TRUE")

    util.create_column(cr, "mail_mass_mailing_contact", "is_email_valid", "boolean")
    cr.execute(
        """
        UPDATE mail_mass_mailing_contact
           SET is_email_valid=TRUE
         WHERE email SIMILAR TO '([^ ,;<@]+@[^> ,;]+)'
    """
    )

    util.create_column(cr, "mail_mail_statistics", "ignored", "timestamp without time zone")
    util.create_column(cr, "mail_mail_statistics", "email", "varchar")

    util.create_column(cr, "res_config_settings", "show_blacklist_buttons", "boolean")
    # ICP = util.env(cr)["ir.config_parameter"]
    # ICP.set_param("mass_mailing.show_blacklist_buttons", False)

    # odoo/odoo@4b3766e8eb05fe4a9f1f083da6f4facf56b4f688
    util.remove_field(cr, "mail.mail.statistics", "recipient")
