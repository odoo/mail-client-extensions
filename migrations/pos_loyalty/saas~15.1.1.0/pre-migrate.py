# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM loyalty_rule WHERE loyalty_program_id IS NULL")
    cr.execute("DELETE FROM loyalty_reward WHERE loyalty_program_id IS NULL")
