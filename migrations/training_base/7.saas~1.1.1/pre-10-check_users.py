from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    users = """
nick_hawson
luke_stason
maria_pulco
thomas_brown
michael_parker
cheryl_jenkings
pete_hurley
greg_fletcher
fred_lafaille
james_fisher
phil_harkins
brandon_light
""".split()
    for u in users:
        if not util.ref('training_base.%s' % u):
            util.remove_record(cr, 'training_base.%s_res_partner' % u, deactivate=True)
