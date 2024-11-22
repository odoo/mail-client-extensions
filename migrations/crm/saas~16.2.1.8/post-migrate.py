from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM crm_lead WHERE email_normalized IS NOT NULL")
    if cr.rowcount:
        ids = [id_ for (id_,) in cr.fetchall()]
        util.recompute_fields(cr, "crm.lead", ["email_domain_criterion"], ids=ids, chunk_size=1024)
