import re

import odoo.upgrade.util.snippets as snip


def convert_device(el):
    el_class_attr = el.get("class", False)
    classes = re.split(r"\s+", el_class_attr)
    if any(class_name.startswith(("d-md-", "d-lg-")) for class_name in classes):
        el.set("class", f"{el_class_attr} o_snippet_mobile_invisible")
        el.set("data-invisible", "1")
        return True

    return False


ANIMATE_OLD_TO_NEW_CLASSES = {
    "o_anim_bounce_in_down": ("o_anim_bounce_in", "o_anim_from_top"),
    "o_anim_bounce_in_left": ("o_anim_bounce_in", "o_anim_from_left"),
    "o_anim_bounce_in_right": ("o_anim_bounce_in", "o_anim_from_right"),
    "o_anim_fade_in_down": ("o_anim_fade_in", "o_anim_from_top"),
    "o_anim_fade_in_left": ("o_anim_fade_in", "o_anim_from_left"),
    "o_anim_fade_in_right": ("o_anim_fade_in", "o_anim_from_right"),
    "o_anim_fade_in_up": ("o_anim_fade_in", "o_anim_from_bottom"),
    "o_anim_rotate_in_down_left": ("o_anim_rotate_in", "o_anim_from_bottom_left"),
    "o_anim_rotate_in_down_right": ("o_anim_rotate_in", "o_anim_from_bottom_right"),
    "o_anim_zoom_in_down": ("o_anim_zoom_in", "o_anim_from_top"),
    "o_anim_zoom_in_left": ("o_anim_zoom_in", "o_anim_from_left"),
    "o_anim_zoom_in_right": ("o_anim_zoom_in", "o_anim_from_right"),
}


def convert_animate(el):
    el_class_attr = el.get("class", False)
    if not el_class_attr:
        return False

    classes = re.split(r"\s+", el_class_attr)

    for class_name in classes:
        new_classes = ANIMATE_OLD_TO_NEW_CLASSES.get(class_name)
        if new_classes is not None:
            classes.remove(class_name)
            classes.extend(new_classes)
            el.set("class", " ".join(classes))
            return True

    if "o_anim_flash" in classes:
        old_style = el.get("style", "")
        el.set("style", f"--wanim-intensity: 100; {old_style}")
        return True

    return False


def migrate(cr, version):
    snip.convert_html_content(
        cr,
        snip.html_converter(convert_device, selector="//*[hasclass('d-none')]"),
        where_column=r"~ '\y(d-md-|d-lg-)'",
    )

    snip.convert_html_content(
        cr,
        snip.html_converter(convert_animate, selector="//*[hasclass('o_animate')]"),
        where_column=r"~ '\yo_animate\y'",
    )
