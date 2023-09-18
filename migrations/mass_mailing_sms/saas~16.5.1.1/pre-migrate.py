# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # create records for {data/demo} subscriptions of contacts to {data/demo} list
    contact_ids = [
        util.ref(cr, f"mass_mailing_sms.mailing_contact_0_{contact_data_id}") for contact_data_id in range(5)
    ]
    demo_list_id = util.ref(cr, "mass_mailing_sms.mailing_list_sms_0")
    if demo_list_id:
        for data_id, contact_id in enumerate(contact_ids):
            if contact_id:
                util.ensure_xmlid_match_record(
                    cr,
                    f"mass_mailing_sms.mailing_list_sms_0_sub_contact_0_{data_id}",
                    "mailing.contact.subscription",
                    {"contact_id": contact_id, "list_id": demo_list_id},
                )
