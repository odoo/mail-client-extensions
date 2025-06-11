from odoo.upgrade import util


def migrate(cr, version):
    if not util.is_changed(cr, "helpdesk.seq_helpdesk_ticket"):
        query = """
            UPDATE helpdesk_ticket
                SET ticket_ref = lpad(ticket_ref, 5, '0')
        """
        util.explode_execute(cr, query, table="helpdesk_ticket")
