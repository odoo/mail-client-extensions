# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # data renaming
    util.rename_xmlid(cr, "crm_iap_mine.seq_crm_iap_lead_mining_request", "crm_iap_mine.ir_sequence_crm_iap_mine")

    # views renaming
    old = "opportunity_tree opportunity_kanban lead_tree lead_kanban".split()
    new = "tree_opportunity kanban_opportunity tree_lead kanban_lead".split()
    for old_xmlpart, new_xmlpart in zip(old, new):
        util.rename_xmlid(cr, f"crm_iap_mine.crm_iap_{old_xmlpart}", f"crm_iap_mine.crm_lead_view_{new_xmlpart}")
    prefix = "crm_iap_lead_mining_request"
    for view_type in "form tree search".split():
        util.rename_xmlid(cr, f"crm_iap_mine.{prefix}_{view_type}", f"crm_iap_mine.{prefix}_view_{view_type}")

    # rename industries / roles / seniorities after being moved with module
    pre = "crm_iap_lead"
    post = "crm_iap_mine"
    suffixes = "30_155 33 69_157 86 114 136 138_156 148 149 150_151 152 153_154 158_159 160 161 162 163 165 166 167 168 238 239"
    for suffix in suffixes.split():
        util.rename_xmlid(cr, f"{post}.{pre}_industry_{suffix}", f"{post}.{post}_industry_{suffix}")
    for suffix in range(1, 23):
        util.rename_xmlid(cr, f"{post}.{pre}_role_{suffix}", f"{post}.{post}_role_{suffix}")
    for suffix in range(1, 4):
        util.rename_xmlid(cr, f"{post}.{pre}_seniority_{suffix}", f"{post}.{post}_seniority_{suffix}")
