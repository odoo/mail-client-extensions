# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "mass_mailing.mass_mailing_contact_0", "mass_mailing.mass_mail_contact_0")
    util.rename_xmlid(cr, "mass_mailing.mass_mail_contact_list_rel_1", "mass_mailing.mailing_list_data_sub_contact_4")
    util.rename_xmlid(cr, "mass_mailing.mass_mail_contact_list_rel_2", "mass_mailing.mailing_list_data_sub_contact_6")
    util.rename_xmlid(cr, "mass_mailing.blacklist_1", "mass_mailing.mail_blacklist_demo_1")

    # create records for {data/demo} subscriptions of contacts to {data/demo} list
    contact_ids = [util.ref(cr, f"mass_mailing.mass_mail_contact_{contact_data_id}") for contact_data_id in range(7)]
    data_list_id = util.ref(cr, "mass_mailing.mailing_list_data")
    if data_list_id:
        for data_id, contact_id in enumerate(contact_ids):
            if contact_id:
                util.ensure_xmlid_match_record(
                    cr,
                    f"mass_mailing.mailing_list_data_sub_contact_{data_id}",
                    "mailing.contact.subscription",
                    {"contact_id": contact_id, "list_id": data_list_id},
                )
    demo_list_id = util.ref(cr, "mass_mailing.mailing_list_1")
    if demo_list_id:
        for data_id, contact_id in enumerate(contact_ids):
            if contact_id:
                util.ensure_xmlid_match_record(
                    cr,
                    f"mass_mailing.mailing_list_1_sub_contact_{data_id}",
                    "mailing.contact.subscription",
                    {"contact_id": contact_id, "list_id": demo_list_id},
                )
