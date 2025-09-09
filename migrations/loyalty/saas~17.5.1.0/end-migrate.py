from odoo.upgrade import util


def migrate(cr, version):
    query = "SELECT id FROM loyalty_reward WHERE description IS NULL"
    util.recompute_fields(cr, "loyalty.reward", ["description"], query=query)
