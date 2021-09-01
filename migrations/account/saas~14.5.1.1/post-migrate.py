# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "account.action_account_resequence")

    # ==========================================================================
    # The Reconciliation Models usability imp (PR: odoo#73043, enterprise#19395)
    # ==========================================================================

    cr.execute("DELETE FROM ir_config_parameter WHERE key='account.disable_rec_models_bypass'")
