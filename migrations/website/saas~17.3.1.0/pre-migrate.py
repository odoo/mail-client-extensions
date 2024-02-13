from odoo.upgrade.util import edit_view


def migrate(cr, version):
    # Adapt the xpath expression to the new OWL SnippetsMenu and remove the
    # d-none xpath as the visibility of the custom snippet section is
    # handled by the SnippetsMenu itself.
    cr.execute(
        """
        SELECT id,
               active
        FROM ir_ui_view
        WHERE key LIKE 'website.snippets.%'
        AND website_id IS NOT NULL
        """
    )
    for view_id, active in cr.fetchall():
        with edit_view(cr, view_id=view_id, active=active) as arch:
            xpath_snippet = arch.find(".//xpath[@expr=\"//div[@id='snippet_custom_body']\"]")
            if xpath_snippet is not None:
                xpath_snippet.attrib["expr"] = "//snippets[@id='snippet_custom']"

            xpath_dnone = arch.find(".//xpath[@expr=\"//div[@id='snippet_custom']\"]")
            if xpath_dnone is not None:
                xpath_dnone.getparent().remove(xpath_dnone)
