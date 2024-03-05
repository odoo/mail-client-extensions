from ast import literal_eval

from odoo.upgrade import util


def migrate(cr, version):
    # Remove all the fields from chatter arch, change the main chatter node from <div class="oe_chatter"/>
    # to <chatter/> and move options from fields to the main node in custom views
    cr.execute(
        r"""
                SELECT id
                  FROM ir_ui_view
                 WHERE type = 'form'
                   AND arch_db->>'en_US' LIKE '%oe\_chatter%'
                   AND arch_db->>'en_US' LIKE ANY(ARRAY['%message\_ids%', '%message\_follower\_ids%'])
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            chatter = util.lxml.etree.Element("chatter")
            for node in arch.xpath('//div[@class="oe_chatter"]'):
                parent = node.getparent()
                for child in node.findall("field") or []:
                    name = child.attrib["name"]
                    try:
                        child_options = literal_eval(child.attrib.get("options", "{}"))
                    except Exception:
                        child_options = {}
                    if not child_options:
                        continue
                    if child_options.get("open_attachments"):
                        chatter.attrib["open_attachments"] = "True"
                    if name == "message_ids":
                        if child_options.get("post_refresh"):
                            chatter.attrib["reload_on_post"] = "True"
                            if child_options["post_refresh"] == "always":
                                chatter.attrib["reload_on_attachment"] = "True"
                    elif name == "message_follower_ids" and child_options.get("post_refresh"):
                        chatter.attrib["reload_on_follower"] = "True"
                parent.replace(node, chatter)
