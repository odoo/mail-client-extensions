# -*- coding: utf-8 -*-


def migrate(cr, version):

    # ==========================================================================
    # The Reconciliation Models usability imp (PR: odoo#73043, enterprise#19395)
    # ==========================================================================

    cr.execute("DELETE FROM ir_config_parameter WHERE key='account.disable_rec_models_bypass'")
