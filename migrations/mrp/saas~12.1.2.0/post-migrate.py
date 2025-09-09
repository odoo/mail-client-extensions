from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE mrp_production
           SET reservation_state='confirmed'
         WHERE reservation_state='waiting'
    """)

    cr.execute("""
        UPDATE mrp_production
           SET reservation_state=NULL
         WHERE reservation_state='none'
            OR state in ('done', 'cancel')
    """)

    query = """
        SELECT id
          FROM mrp_production
         WHERE state='progress'
    """
    util.recompute_fields(cr, "mrp.production", ["state"], query=query)

    query = """
        SELECT id
          FROM mrp_production
         WHERE reservation_state='partially_available'
    """
    util.recompute_fields(cr, "mrp.production", ["reservation_state"], query=query)

    cr.execute("""
        UPDATE mrp_workorder w
           SET production_availability = p.reservation_state
          FROM mrp_production p
         WHERE w.production_id=p.id
    """)
