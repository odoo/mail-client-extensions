# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})
    rt2 = dict(reset_translations={"subject", "body_html", "report_name"})

    util.if_unchanged(cr, "sale_subscription.email_payment_close", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "sale_subscription.email_payment_reminder", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "sale_subscription.email_payment_success", util.update_record_from_xml, **rt2)
    util.if_unchanged(cr, "sale_subscription.mail_template_subscription_rating", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "sale_subscription.mail_template_subscription_alert", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "sale_subscription.mail_template_subscription_invoice", util.update_record_from_xml, **rt2)

    rt_sms = dict(reset_translations={"body"})
    util.if_unchanged(cr, "sale_subscription.sms_template_data_default_alert", util.update_record_from_xml, **rt_sms)
    util.if_unchanged(cr, "sale_subscription.sms_template_data_payment_failure", util.update_record_from_xml, **rt_sms)
    util.if_unchanged(cr, "sale_subscription.sms_template_data_payment_reminder", util.update_record_from_xml, **rt_sms)
