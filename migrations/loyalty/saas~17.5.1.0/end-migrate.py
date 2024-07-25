from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM loyalty_reward WHERE description IS NULL")
    util.recompute_fields(cr, "loyalty.reward", ["description"], ids=[row[0] for row in cr.fetchall()])
