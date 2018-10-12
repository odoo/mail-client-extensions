# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "hr.contract", *eb("sign{ature,}_request_ids"))
    cr.execute("ALTER TABLE hr_contract_signature_request_rel RENAME TO hr_contract_sign_request_rel")
    cr.execute("ALTER TABLE hr_contract_sign_request_rel RENAME COLUMN signature_request_id TO sign_request_id")
    util.rename_field(cr, "hr.contract", *eb("sign{ature,}_request_count"))
    util.rename_field(cr, "hr.contract", *eb("sign{ature_request,}_template_id"))

    util.rename_xmlid(cr, *eb("hr_contract_salary.{signature_item_party,sign_item_role}_job_responsible"))
    util.remove_record(cr, "hr_contract_salary.mail_template_data_notification_email_send_offer")
