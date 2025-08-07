from odoo.upgrade import util


def migrate(cr, version):
    def intrastat_domain_adapter(leaf, _or, _neg):
        _, op, right = leaf
        if op not in ("=", "!="):
            return [leaf]
        if not right:
            op = "!=" if op == "=" else "="
        return [("country_group_ids.code", op, "INTRASTAT")]

    util.adapt_domains(cr, "res.country", "intrastat", "country_group_ids.code", intrastat_domain_adapter)
    util.remove_field(cr, "res.country", "intrastat")
    util.remove_view(cr, "account_intrastat.view_country_form")
    util.remove_view(cr, "account_intrastat.view_country_tree")
