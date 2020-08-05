# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents_sign.documents_workflow_action_sign_request")
    util.remove_record(cr, "documents_sign.documents_sign_rule_sign_request")
    util.remove_record(cr, "documents_sign.documents_workflow_action_sign_request_finance")
    util.remove_record(cr, "documents_sign.documents_sign_rule_sign_request_finance")
