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
        login = u.split('_')[0] + '@openwood.com'
        xmlid = 'training_base.' + u
        if not util.ensure_xmlid_match_record(cr, xmlid, 'res.users', {'login': login}):
            util.delete_unused(cr, 'training_base.%s_res_partner' % u, deactivate=True)
