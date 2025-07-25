from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "industry_fsm.fsm_customer_ratings_server_action")
