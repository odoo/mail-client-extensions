from odoo import models

from odoo.addons.documents.models import tags  # noqa


def migrate(cr, version):
    pass


class Tags(models.Model):
    _inherit = "documents.tag"
    _module = "documents"
    _match_uniq = True


class TagsCategories(models.Model):
    _inherit = "documents.facet"
    _module = "documents"
    _match_uniq = True
