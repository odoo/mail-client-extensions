# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Since pos_loyalty may now depend on loyalty(starting saas~15.3), loyalty's migration might have already
    #  started, in that case it was already handled by loyalty's pre-migrate.
    if util.table_exists(cr, "pos_loyalty_program"):
        return
    if util.column_exists(cr, "loyalty_rule", "loyalty_program_id"):
        cr.execute("DELETE FROM loyalty_rule WHERE loyalty_program_id IS NULL")
        cr.execute("DELETE FROM loyalty_reward WHERE loyalty_program_id IS NULL")
