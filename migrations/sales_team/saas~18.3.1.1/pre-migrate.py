from odoo.upgrade import util


def migrate(cr, version):
    # set "random" value if never set to avoid only old teams not having colors
    cr.execute("""
        UPDATE crm_team
           SET color=(id % 11) + 1
         WHERE color IS NULL
    """)
    util.remove_field(cr, "crm.team", "dashboard_graph_data")
