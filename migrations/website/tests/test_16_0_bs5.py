# -*- coding: utf-8 -*-
import logging

from lxml import etree

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

_logger = logging.getLogger("odoo.upgrade.website.tests." + __name__)


@change_version("16.0")
class TestBS4ToBS5(UpgradeCase):
    def _get_chunks(self, which):
        # Not included:
        # card-columns => Masonry plugin.

        chunks = [
            [
                """<button class="close" data-dismiss="alert"/>""",
                """<button class="btn-close" data-bs-dismiss="alert"/>""",
            ],
            [
                """<button t-att-class="'close'" data-dismiss="alert"/>""",
                """<button t-att-class="'btn-close'" data-bs-dismiss="alert"/>""",
            ],
            [
                """<button t-attf-class="close" data-dismiss="alert"/>""",
                """<button t-attf-class="btn-close" data-bs-dismiss="alert"/>""",
            ],
            [
                """<div data-toggle="collapse" data-display="static" data-spy="scroll"/>""",
                """<div data-bs-toggle="collapse" data-bs-display="static" data-bs-spy="scroll"/>""",
            ],
            [
                """<div data-interval="5000" data-original-title="Title" data-parent="#abc"/>""",
                """<div data-bs-interval="5000" data-bs-original-title="Title" data-bs-parent="#abc"/>""",
            ],
            [
                """<div data-dismiss="" data-backdrop="" data-ride=""/>""",
                """<div data-bs-dismiss="" data-bs-backdrop="" data-bs-ride=""/>""",
            ],
            [
                """<div data-slide="" data-slide-to="" data-placement=""/>""",
                """<div data-bs-slide="" data-bs-slide-to="" data-bs-placement=""/>""",
            ],
            [
                """<div t-att-data-toggle="collapse" t-att-data-display="'static'" t-att-data-spy="'scroll'"/>""",
                """<div t-att-data-bs-toggle="collapse" t-att-data-bs-display="'static'" t-att-data-bs-spy="'scroll'"/>""",
            ],
            [
                """<div t-att-data-interval="'5000'" t-att-data-original-title="'Title'" t-att-data-parent="#abc"/>""",
                """<div t-att-data-bs-interval="'5000'" t-att-data-bs-original-title="'Title'" t-att-data-bs-parent="#abc"/>""",
            ],
            [
                """<div t-att-data-dismiss="''" t-att-data-backdrop="''" t-att-data-ride="''"/>""",
                """<div t-att-data-bs-dismiss="''" t-att-data-bs-backdrop="''" t-att-data-bs-ride="''"/>""",
            ],
            [
                """<div t-att-data-slide="''" t-att-data-slide-to="''" t-att-data-placement=""/>""",
                """<div t-att-data-bs-slide="''" t-att-data-bs-slide-to="''" t-att-data-bs-placement=""/>""",
            ],
            [
                """<div t-attf-data-toggle="collapse" t-attf-data-display="static" t-attf-data-spy="scroll"/>""",
                """<div t-attf-data-bs-toggle="collapse" t-attf-data-bs-display="static" t-attf-data-bs-spy="scroll"/>""",
            ],
            [
                """<div t-attf-data-interval="5000" t-attf-data-original-title="Title" t-attf-data-parent="#abc"/>""",
                """<div t-attf-data-bs-interval="5000" t-attf-data-bs-original-title="Title" t-attf-data-bs-parent="#abc"/>""",
            ],
            [
                """<div t-attf-data-dismiss="" t-attf-data-backdrop="" t-attf-data-ride=""/>""",
                """<div t-attf-data-bs-dismiss="" t-attf-data-bs-backdrop="" t-attf-data-bs-ride=""/>""",
            ],
            [
                """<div t-attf-data-slide="" t-attf-data-slide-to="" t-attf-data-placement=""/>""",
                """<div t-attf-data-bs-slide="" t-attf-data-bs-slide-to="" t-attf-data-bs-placement=""/>""",
            ],
            ["""<span class="badge-pill">Badge</span>""", """<span class="rounded-pill">Badge</span>"""],
            [
                """
<form>
    <div class="form-row">
        <label for="test"/>
        <input id="test"/>
    </div>
</form>
                """,
                """
<form>
    <div class="row">
        <label for="test" class="form-label"/>
        <input id="test"/>
    </div>
</form>
                """,
            ],
            [
                """
<table>
    <thead class="thead-light"/>
    <tbody/>
</table>
                """,
                """
<table>
    <thead class="table-light"/>
    <tbody/>
</table>
                """,
            ],
            [
                """
<table>
    <thead class="thead-dark"/>
    <tbody/>
</table>
                """,
                """
<table>
    <thead class="table-dark"/>
    <tbody/>
</table>
                """,
            ],
            [
                """
<form>
    <div class="input-group mb-3">
        <div class="input-group-prepend">
            <span class="input-group-text">$</span>
        </div>
        <input type="text" class="form-control" aria-label="Amount (to the nearest dollar)"/>
        <div class="input-group-append">
            <span class="input-group-text">.00</span>
        </div>
    </div>
</form>
                """,
                """
<form>
    <div class="input-group mb-3">
        <span class="input-group-text">$</span>
        <input type="text" class="form-control" aria-label="Amount (to the nearest dollar)"/>
        <span class="input-group-text">.00</span>
    </div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="custom-control custom-checkbox">
        <input type="checkbox" class="custom-control-input" id="customCheck1"/>
        <label class="custom-control-label" for="customCheck1">Check this custom checkbox</label>
    </div>
</form>
                """,
                """
<form>
    <div class="form-check">
        <input type="checkbox" class="form-check-input" id="customCheck1"/>
        <label class="form-check-label" for="customCheck1">Check this custom checkbox</label>
    </div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="form-group">
        <select class="custom-select">
            <option value="">Open this select menu</option>
            <option value="1">One</option>
            <option value="2">Two</option>
            <option value="3">Three</option>
        </select>
        <div class="invalid-feedback">Example invalid custom select feedback</div>
    </div>
</form>
                """,
                """
<form class="row">
    <div class="col-12 py-2">
        <select class="form-select">
            <option value="">Open this select menu</option>
            <option value="1">One</option>
            <option value="2">Two</option>
            <option value="3">Three</option>
        </select>
        <div class="invalid-feedback">Example invalid custom select feedback</div>
    </div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="custom-file">
        <input type="file" class="custom-file-input" id="validatedCustomFile"/>
        <label class="custom-file-label" for="validatedCustomFile">Choose file...</label>
        <div class="invalid-feedback">Example invalid custom file feedback</div>
    </div>
</form>
                """,
                """
<form>
    <input type="file" class="form-control" id="validatedCustomFile"/>
    <div class="invalid-feedback">Example invalid custom file feedback</div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="form-group">
        <label for="customRange1">Example range</label>
        <input type="range" class="custom-range" id="customRange1"/>
    </div>
</form>
                """,
                """
<form class="row">
    <div class="col-12 py-2">
        <label for="customRange1" class="form-label">Example range</label>
        <input type="range" class="form-range" id="customRange1"/>
    </div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="custom-control custom-radio">
        <input type="radio" class="custom-control-input" id="customControlValidation2" name="radio-stacked"/>
        <label class="custom-control-label" for="customControlValidation2">Toggle this custom radio</label>
    </div>
    <div class="custom-control custom-radio mb-3">
        <input type="radio" class="custom-control-input" id="customControlValidation3" name="radio-stacked"/>
        <label class="custom-control-label" for="customControlValidation3">Or toggle this other custom radio</label>
        <div class="invalid-feedback">More example invalid feedback text</div>
    </div>
</form>
                """,
                """
<form>
    <div class="form-check">
        <input type="radio" class="form-check-input" id="customControlValidation2" name="radio-stacked"/>
        <label class="form-check-label" for="customControlValidation2">Toggle this custom radio</label>
    </div>
    <div class="form-check mb-3">
        <input type="radio" class="form-check-input" id="customControlValidation3" name="radio-stacked"/>
        <label class="form-check-label" for="customControlValidation3">Or toggle this other custom radio</label>
        <div class="invalid-feedback">More example invalid feedback text</div>
    </div>
</form>
                """,
            ],
            [
                """
<form>
    <div class="custom-control custom-switch">
        <input type="checkbox" class="custom-control-input" id="customSwitch1"/>
        <label class="custom-control-label" for="customSwitch1">Toggle this switch element</label>
    </div>
</form>
                """,
                """
<form>
    <div class="form-check form-switch">
        <input type="checkbox" class="form-check-input" id="customSwitch1"/>
        <label class="form-check-label" for="customSwitch1">Toggle this switch element</label>
    </div>
</form>
                """,
            ],
            [
                """
<a href="#" class="text-danger">text-danger</a>
<a href="#" class="text-o-color-4">text-danger</a>
                """,
                """
<a href="#" class="link-danger">text-danger</a>
<a href="#" class="text-o-color-4">text-danger</a>
                """,
            ],
            [
                """
<div>
    <button class="btn btn-block"/>
</div>
<p>
    <button class="btn btn-block"/>
</p>
<p>
    <span>something else</span>
    <button class="btn btn-block"/>
</p>
                """,
                """
<div class="d-grid gap-2">
    <button class="btn"/>
</div>
<p class="d-grid gap-2">
    <button class="btn"/>
</p>
<p>
    <span>something else</span>
    <button class="btn"/>
</p>
                """,
            ],
            [
                """<div class="left-SIZE-0 right-SIZE-100">Left-right</div>""",
                """<div class="start-SIZE-0 end-SIZE-100">Left-right</div>""",
            ],
            ["""<div class="float-left">float-left</div>""", """<div class="float-start">float-left</div>"""],
            ["""<div class="float-right">float-right</div>""", """<div class="float-end">float-right</div>"""],
            ["""<div class="border-left">border-left</div>""", """<div class="border-start">border-left</div>"""],
            ["""<div class="border-right">border-right</div>""", """<div class="border-end">border-right</div>"""],
            [
                """<div class="ml-SIZE-2 mr-SIZE-4 pl-SIZE-8 pr-SIZE-16">Margins and paddings</div>""",
                """<div class="ms-SIZE-2 me-SIZE-4 ps-SIZE-8 pe-SIZE-16">Margins and paddings</div>""",
            ],
            ["""<div class="text-left">text-left</div>""", """<div class="text-start">text-left</div>"""],
            ["""<div class="text-right">text-right</div>""", """<div class="text-end">text-right</div>"""],
            ["""<div class="dropdown-menu-left"/>""", """<div class="dropdown-menu-start"/>"""],
            ["""<div class="dropdown-menu-right"/>""", """<div class="dropdown-menu-end"/>"""],
            ["""<div class="dropleft"/>""", """<div class="dropstart"/>"""],
            ["""<div class="dropright"/>""", """<div class="dropend"/>"""],
            [
                """<div class="text-monospace font-weight-bold font-style-italic"/>""",
                """<div class="font-monospace fw-bold fst-italic"/>""",
            ],
            ["""<div class="font-italic"/>""", """<div class="fst-italic"/>"""],
            ["""<div class="badge-danger"/>""", """<div class="text-bg-danger"/>"""],
            [
                """
<a href="#" data-toggle="tooltip" title="Some tooltip text!">Hover over me</a>
<div class="tooltip bs-tooltip-top" role="tooltip">
    <div class="arrow"></div>
    <div class="tooltip-inner">
        Some tooltip text!
    </div>
</div>
                """,
                """
<a href="#" data-bs-toggle="tooltip" title="Some tooltip text!">Hover over me</a>
<div class="tooltip bs-tooltip-top" role="tooltip">
    <div class="tooltip-arrow"></div>
    <div class="tooltip-inner">
        Some tooltip text!
    </div>
</div>
                """,
            ],
            [
                """
<div class="popover" role="tooltip">
    <div class="arrow"></div>
    <h3 class="popover-header"></h3>
    <div class="popover-body"></div>
</div>
                """,
                """
<div class="popover" role="tooltip">
    <div class="popover-arrow"></div>
    <h3 class="popover-header"></h3>
    <div class="popover-body"></div>
</div>
                """,
            ],
            ["""<div class="no-gutters"/>""", """<div class="g-0"/>"""],
            ["""<div class="embed-responsive embed-responsive-1by2"/>""", """<div class="ratio ratio-1x2"/>"""],
            ["""<div class="ratio-1by2"/>""", """<div class="ratio-1x2"/>"""],
            [
                """<div class="sr-only sr-only-focusable"/>""",
                """<div class="visually-hidden visually-hidden-focusable"/>""",
            ],
            [
                """<div class="media media-body"/>""",
                """<div class="d-flex flex-grow-1"/>""",
            ],
            ["""<div class="rounded-left rounded-right"/>""", """<div class="rounded-start rounded-end"/>"""],
            ["""<div class="rounded-sm-left rounded-sm-right"/>""", """<div class="rounded-start-1 rounded-end-1"/>"""],
            ["""<div class="rounded-lg-left rounded-lg-right"/>""", """<div class="rounded-start-3 rounded-end-3"/>"""],
            [
                """<div class="col-sm-offset-1 col-md-offset-2 col-lg-offset-3"/>""",
                """<div class="offset-sm-1 offset-md-2 offset-lg-3"/>""",
            ],
            [
                """<div class="col-SIZE-offset-4"/>""",
                """<div class="offset-SIZE-4"/>""",
            ],
            [
                """
<ul class="navbar-nav">
    <li class="nav-item active">
        <a class="nav-link" href="#">Active link</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="#">Non-active link</a>
    </li>
</ul>
                """,
                """
<ul class="navbar-nav">
    <li class="nav-item">
        <a class="nav-link active" href="#">Active link</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="#">Non-active link</a>
    </li>
</ul>
                """,
            ],
            [
                """
<div class="jumbotron">
    <h1 class="display-4">Hello, world!</h1>
    <p class="lead">Some text.</p>
    <hr class="my-4"/>
    <p>More text.</p>
    <p class="lead">
        <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
    </p>
</div>
                """,
                """
<div class="container-fluid py-5">
    <h1 class="display-4">Hello, world!</h1>
    <p class="lead">Some text.</p>
    <hr class="my-4"/>
    <p>More text.</p>
    <p class="lead">
        <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
    </p>
</div>
                """,
            ],
            [
                """
<div class="card-deck">
    <div class="card">
        <img src="/favicon.ico" class="card-img-top" alt="..."/>
        <div class="card-body">
            <h5 class="card-title">First title</h5>
            <p class="card-text">First content.</p>
        </div>
        <div class="card-footer">
            <small class="text-muted">First footer</small>
        </div>
    </div>
    <div class="card">
        <img src="/favicon.ico" class="card-img-top" alt="..."/>
        <div class="card-body">
            <h5 class="card-title">Second title</h5>
            <p class="card-text">Second content.</p>
        </div>
        <div class="card-footer">
            <small class="text-muted">Second footer</small>
        </div>
    </div>
</div>
                """,
                """
<div class="row row-cols-2">
    <div class="col">
        <div class="card">
            <img src="/favicon.ico" class="card-img-top" alt="..."/>
            <div class="card-body">
                <h5 class="card-title">First title</h5>
                <p class="card-text">First content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">First footer</small>
            </div>
        </div>
    </div>
    <div class="col">
        <div class="card">
            <img src="/favicon.ico" class="card-img-top" alt="..."/>
            <div class="card-body">
                <h5 class="card-title">Second title</h5>
                <p class="card-text">Second content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Second footer</small>
            </div>
        </div>
    </div>
</div>
                """,
            ],
            [
                """
<div class="card-deck">
    <div class="card">
        <img src="/favicon.ico" class="card-img-top" alt="..."/>
        <div class="card-body">
            <h5 class="card-title">First title</h5>
            <p class="card-text">First content.</p>
        </div>
        <div class="card-footer">
            <small class="text-muted">First footer</small>
        </div>
    </div>
    <div class="card">
        <img src="/favicon.ico" class="card-img-top" alt="..."/>
        <div class="card-body">
            <h5 class="card-title">Second title</h5>
            <p class="card-text">Second content.</p>
        </div>
        <div class="card-footer">
            <small class="text-muted">Second footer</small>
        </div>
    </div>
    <div class="card">
        <img src="/favicon.ico" class="card-img-top" alt="..."/>
        <div class="card-body">
            <h5 class="card-title">Third title</h5>
            <p class="card-text">Third content.</p>
        </div>
        <div class="card-footer">
            <small class="text-muted">Third footer</small>
        </div>
    </div>
</div>
                """,
                """
<div class="row row-cols-3">
    <div class="col">
        <div class="card">
            <img src="/favicon.ico" class="card-img-top" alt="..."/>
            <div class="card-body">
                <h5 class="card-title">First title</h5>
                <p class="card-text">First content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">First footer</small>
            </div>
        </div>
    </div>
    <div class="col">
        <div class="card">
            <img src="/favicon.ico" class="card-img-top" alt="..."/>
            <div class="card-body">
                <h5 class="card-title">Second title</h5>
                <p class="card-text">Second content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Second footer</small>
            </div>
        </div>
    </div>
    <div class="col">
        <div class="card">
            <img src="/favicon.ico" class="card-img-top" alt="..."/>
            <div class="card-body">
                <h5 class="card-title">Third title</h5>
                <p class="card-text">Third content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Third footer</small>
            </div>
        </div>
    </div>
</div>
                """,
            ],
            [
                """
<form class="form-inline">
    <label class="sr-only" for="inlineFormInputName2">Name</label>
    <input type="text" class="form-control mb-2 mr-sm-2" id="inlineFormInputName2" placeholder="Jane Doe"/>

    <label class="sr-only" for="inlineFormInputGroupUsername2">Username</label>
    <div class="input-group mb-2 mr-sm-2">
        <div class="input-group-prepend">
            <div class="input-group-text">@</div>
        </div>
        <input type="text" class="form-control" id="inlineFormInputGroupUsername2" placeholder="Username"/>
    </div>

    <div class="form-check mb-2 mr-sm-2">
        <input class="form-check-input" type="checkbox" id="inlineFormCheck"/>
        <label class="form-check-label" for="inlineFormCheck">Remember me</label>
    </div>

    <button type="submit" class="btn btn-primary mb-2">Submit</button>
</form>
                """,
                """
<form class="row row-cols-lg-auto">
    <div class="col-12">
        <label class="visually-hidden form-label" for="inlineFormInputName2">Name</label>
        <input type="text" class="form-control mb-2 me-sm-2" id="inlineFormInputName2" placeholder="Jane Doe"/>
    </div>

    <div class="col-12">
        <label class="visually-hidden form-label" for="inlineFormInputGroupUsername2">Username</label>
        <div class="input-group mb-2 me-sm-2">
            <div class="input-group-text">@</div>
            <input type="text" class="form-control" id="inlineFormInputGroupUsername2" placeholder="Username"/>
        </div>
    </div>

    <div class="col-12">
        <div class="form-check mb-2 me-sm-2">
            <input class="form-check-input" type="checkbox" id="inlineFormCheck"/>
            <label class="form-check-label" for="inlineFormCheck">Remember me</label>
        </div>
    </div>

    <div class="col-12">
        <button type="submit" class="btn btn-primary mb-2">Submit</button>
    </div>
</form>
                """,
            ],
            ["""<input type="file" class="form-control-file"/>""", """<input type="file" class="form-control"/>"""],
            ["""<input type="range" class="form-control-range"/>""", """<input type="range" class="form-range"/>"""],
        ]
        all_chunks = []
        for chunk_versions in chunks:
            chunk = chunk_versions[which]
            if "-SIZE" in chunk:
                for size in ["", "-sm", "-md", "-lg", "-xl"]:
                    all_chunks.append(chunk.replace("-SIZE", size))
            else:
                all_chunks.append(chunk)
        return all_chunks

    def prepare(self):
        View = self.env["ir.ui.view"]

        bs_debug_15_3_arch = """
<t name="Debug for test" t-name="website.bs_debug_page_view_for_test">
    <t t-call="website.layout">
        <t t-set="odoo_theme_colors" t-value="[['o-color-1', 'Color 1'], ['o-color-2', 'Color 2'],
['o-color-3', 'Color 3'], ['o-color-4', 'Color 4'], ['o-color-5', 'Color 5']]"/>
        <t t-set="bs_theme_colors" t-value="[['primary', 'Primary'], ['secondary', 'Secondary'],
['success', 'Success'], ['info', 'Info'], ['warning', 'Warning'], ['danger', 'Danger'],
['light', 'Light'], ['dark', 'Dark']]"/>
        <t t-set="bs_gray_colors" t-value="[['white', 'White'], ['100', '100'], ['200', '200'],
['300', '300'], ['400', '400'], ['500', '500'], ['600', '600'], ['700', '700'], ['800', '800'],
['900', '900'], ['black', 'Black']]"/>
        <div id="wrap" class="oe_structure">
            <section class="py-2">
                <div class="container">
                    <h1>Components</h1>
                    <div class="row">
                        <div class="col-md">
                            <h2>Badge</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <span t-attf-class="badge mb-1 badge-#{color[0]}"><t t-esc="color[1]"/></span>
                            </t>
                            <h3 class="mt-2 h6">Pill</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <span t-attf-class="badge mb-1 badge-pill badge-#{color[0]}"><t t-esc="color[1]"/></span>
                            </t>
                            <h3 class="mt-2 h6">Link</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <a href="#" t-attf-class="badge mb-1 badge-#{color[0]}"><t t-esc="color[1]"/></a>
                            </t>
                            <h3 class="mt-2 h6">Autosizing</h3>
                            <div class="h3">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <span t-attf-class="badge mb-1 badge-#{color[0]}"><t t-esc="color[1]"/></span>
                                </t>
                            </div>

                            <h2 class="mt-4">Button</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Outline</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-outline-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Small</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-sm btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Large</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-lg btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>

                            <h2 class="mt-4">Dropdown</h2>
                            <div class="dropdown">
                                <button type="button" class="btn btn-primary dropdown-toggle"
data-toggle="dropdown">Toggle</button>
                                <div class="dropdown-menu">
                                    <div class="dropdown-header">Header</div>
                                    <a class="dropdown-item" href="#">Action</a>
                                    <a class="dropdown-item" href="#">Something else here</a>
                                    <div class="dropdown-divider"/>
                                    <a class="dropdown-item" href="#">Separated link</a>
                                </div>
                            </div>

                            <h2 class="mt-4">Navbar</h2>
                            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                                <a class="navbar-brand" href="#">Navbar</a>
                                <button class="navbar-toggler" type="button" data-toggle="collapse"
data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
aria-label="Toggle navigation">
                                <span class="navbar-toggler-icon"></span>
                                </button>

                                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                                    <ul class="navbar-nav mr-auto">
                                        <li class="nav-item active">
                                            <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
                                        </li>
                                        <li class="nav-item">
                                            <a class="nav-link" href="#">Link</a>
                                        </li>
                                        <li class="nav-item">
                                            <a class="nav-link disabled" href="#">Disabled</a>
                                        </li>
                                    </ul>
                                    <form class="form-inline my-2 my-lg-0">
                                        <input class="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search"/>
                                        <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
                                    </form>
                                </div>
                            </nav>

                            <h2 class="mt-4">Form</h2>
                            <form>
                                <div class="form-group">
                                    <label for="exampleInputEmail1">Email address</label>
                                    <input type="email" class="form-control" id="exampleInputEmail1"
aria-describedby="emailHelp" placeholder="Enter email"/>
                                    <small id="emailHelp" class="form-text text-muted">
We'll never share your email with anyone else.</small>
                                </div>
                            </form>

                            <h2 class="mt-4">Pagination</h2>
                            <nav>
                                <ul class="pagination">
                                    <li class="page-item disabled">
                                        <a class="page-link" href="#" tabindex="-1">Previous</a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">1</a>
                                    </li>
                                    <li class="page-item active">
                                        <a class="page-link" href="#">2 <span class="sr-only">(current)</span></a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">3</a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">Next</a>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                        <div class="col-md-auto">
                            <h2>Alert</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <div t-attf-class="alert alert-#{color[0]}">
                                    This is a "<t t-esc="color[1]"/>" alert with a <a href="#" class="alert-link">link</a>.
                                </div>
                            </t>

                            <h2 class="mt-4">Breadcrumb</h2>
                            <nav aria-label="breadcrumb">
                                <ol class="breadcrumb">
                                    <li class="breadcrumb-item"><a href="#">Home</a></li>
                                    <li class="breadcrumb-item"><a href="#">Library</a></li>
                                    <li class="breadcrumb-item active" aria-current="page">Data</li>
                                </ol>
                            </nav>

                            <h2 class="mt-4">Card</h2>
                            <div class="card">
                                <div class="card-header">
                                    Card Header
                                </div>
                                <div class="card-body">
                                    Card Body
                                </div>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item">Item 1</li>
                                    <li class="list-group-item">Item 2</li>
                                </ul>
                                <div class="card-footer">
                                    Card Footer
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <section class="py-2">
                <div class="container">
                    <h1>Utilities &amp; Typography</h1>
                    <div class="row">
                        <div class="col-md">
                            <div class="row no-gutters">
                                <t t-foreach="odoo_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row no-gutters mt-2">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row no-gutters mt-2">
                                <t t-foreach="bs_gray_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row no-gutters mt-4">
                                <t t-foreach="odoo_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row no-gutters mt-2">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row no-gutters mt-2">
                                <t t-foreach="bs_gray_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                        </div>
                        <div class="col-md-auto">
                            <h1>Headings 1</h1>
                            <h2>Headings 2</h2>
                            <h3>Headings 3</h3>
                            <h4>Headings 4</h4>
                            <h5>Headings 5</h5>
                            <h6>Headings 6</h6>
                            <p>Paragraph with <strong>bold</strong>, <span class="text-muted">
muted</span> and <em>italic</em> texts</p>
                            <p><a href="#">Link</a></p>
                            <p><button type="button" class="btn btn-link">Link button</button></p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>
        """
        debug_view = View.create(
            {
                "name": "BS Debug Test",
                "type": "qweb",
                "arch": bs_debug_15_3_arch,
                "website_id": 1,
            }
        )

        arch = "<!-- Separator -->".join(
            [
                """
<t name="BS4 to BS5 test" t-name="website.bs_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'bs_test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_test" data-snippet="s_test" data-name="Test" style="background-image: none;">
        <div class="container">
          <div class="row">
            <div class="col-12">
            """,
                *self._get_chunks(0),
                """
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>
            """,
            ]
        )

        test_view = View.create(
            {
                "name": "BS4 to BS5 Test",
                "type": "qweb",
                "arch": arch.replace(r"\n", ""),
                "website_id": 1,
            }
        )

        # Testing that forking a view and modifying it makes it converted to
        # bootstrap 5 but forking a view and not modifying it makes it updated
        # to the 16.0 version.
        Website = self.env["website"]
        website_a = Website.create({"name": "Website A"})
        website_b = Website.create({"name": "Website B"})
        # Note: this test is true with any view but to test properly, we need
        # one who had non-bootstrap changes between 15.X and 16.0. Here, one
        # unlikely to change in stable on its "oe_structure" element was chosen.
        generic_view = self.env.ref("website.show_website_info")
        generic_view.with_context(website_id=website_a.id).write(
            {
                "arch": generic_view.arch.replace(
                    '<div class="oe_structure">', '<div class="oe_structure text-left">', 1
                ),
            }
        )
        generic_view.with_context(website_id=website_b.id).write(
            {
                "active": not generic_view.active,
            }
        )
        specific_views = View.with_context(active_test=False).search(
            [
                ("key", "=", "website.show_website_info"),
                ("website_id", "!=", False),
            ]
        )

        return {
            "debug_view_id": debug_view.id,
            "test_view_id": test_view.id,
            "generic_view_id": generic_view.id,
            "old_generic_view_arch": generic_view.arch,
            "touched_specific_view_id": specific_views.filtered(lambda v: v.website_id.id == website_a.id).id,
            "untouched_specific_view_id": specific_views.filtered(lambda v: v.website_id.id == website_b.id).id,
        }

    def _reformat(self, arch, is_html=False):
        parser = etree.HTMLParser(remove_blank_text=True) if is_html else etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(f"<wrap>{arch}</wrap>", parser=parser)
        wrap_node = tree.xpath("//wrap")[0]
        return "\n".join(
            etree.tostring(child, encoding="unicode", pretty_print=True, method="html" if is_html else None)
            for child in wrap_node
        ).strip()

    def check(self, init):
        bs_debug_16_0_arch = """
<t name="Debug for test" t-name="website.bs_debug_page_view_for_test">
    <t t-call="website.layout">
        <t t-set="odoo_theme_colors" t-value="[['o-color-1', 'Color 1'], ['o-color-2', 'Color 2'],
['o-color-3', 'Color 3'], ['o-color-4', 'Color 4'], ['o-color-5', 'Color 5']]"/>
        <t t-set="bs_theme_colors" t-value="[['primary', 'Primary'], ['secondary', 'Secondary'],
['success', 'Success'], ['info', 'Info'], ['warning', 'Warning'], ['danger', 'Danger'],
['light', 'Light'], ['dark', 'Dark']]"/>
        <t t-set="bs_gray_colors" t-value="[['white', 'White'], ['100', '100'], ['200', '200'],
['300', '300'], ['400', '400'], ['500', '500'], ['600', '600'], ['700', '700'], ['800', '800'],
['900', '900'], ['black', 'Black']]"/>
        <div id="wrap" class="oe_structure">
            <section class="py-2">
                <div class="container">
                    <h1>Components</h1>
                    <div class="row">
                        <div class="col-md">
                            <h2>Badge</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <span t-attf-class="badge mb-1 text-bg-#{color[0]}"><t t-esc="color[1]"/></span>
                            </t>
                            <h3 class="mt-2 h6">Pill</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <span t-attf-class="badge mb-1 rounded-pill text-bg-#{color[0]}"><t t-esc="color[1]"/></span>
                            </t>
                            <h3 class="mt-2 h6">Link</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <a href="#" t-attf-class="badge mb-1 text-bg-#{color[0]}"><t t-esc="color[1]"/></a>
                            </t>
                            <h3 class="mt-2 h6">Autosizing</h3>
                            <div class="h3">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <span t-attf-class="badge mb-1 text-bg-#{color[0]}"><t t-esc="color[1]"/></span>
                                </t>
                            </div>

                            <h2 class="mt-4">Button</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Outline</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-outline-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Small</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-sm btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>
                            <h3 class="mt-2 h6">Large</h3>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <button type="button" t-attf-class="btn mb-1 btn-lg btn-#{color[0]}"><t t-esc="color[1]"/></button>
                            </t>

                            <h2 class="mt-4">Dropdown</h2>
                            <div class="dropdown">
                                <button type="button" class="btn btn-primary dropdown-toggle"
data-bs-toggle="dropdown">Toggle</button>
                                <div class="dropdown-menu">
                                    <div class="dropdown-header">Header</div>
                                    <a class="dropdown-item" href="#">Action</a>
                                    <a class="dropdown-item" href="#">Something else here</a>
                                    <div class="dropdown-divider"/>
                                    <a class="dropdown-item" href="#">Separated link</a>
                                </div>
                            </div>

                            <h2 class="mt-4">Navbar</h2>
                            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                                <a class="navbar-brand" href="#">Navbar</a>
                                <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
aria-label="Toggle navigation">
                                <span class="navbar-toggler-icon"></span>
                                </button>

                                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                                    <ul class="navbar-nav me-auto">
                                        <li class="nav-item">
                                            <a class="nav-link active"
                                               href="#">Home <span class="visually-hidden">(current)</span></a>
                                        </li>
                                        <li class="nav-item">
                                            <a class="nav-link" href="#">Link</a>
                                        </li>
                                        <li class="nav-item">
                                            <a class="nav-link disabled" href="#">Disabled</a>
                                        </li>
                                    </ul>
                                    <form class="row row-cols-lg-auto my-2 my-lg-0">
                                        <div class="col-12">
                                            <input class="form-control me-sm-2" type="search"
                                                   placeholder="Search" aria-label="Search"/>
                                        </div>
                                        <div class="col-12">
                                            <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
                                        </div>
                                    </form>
                                </div>
                            </nav>

                            <h2 class="mt-4">Form</h2>
                            <form class="row">
                                <div class="col-12 py-2">
                                    <label for="exampleInputEmail1" class="form-label">Email address</label>
                                    <input type="email" class="form-control" id="exampleInputEmail1"
aria-describedby="emailHelp" placeholder="Enter email"/>
                                    <small id="emailHelp" class="form-text text-muted">
We'll never share your email with anyone else.</small>
                                </div>
                            </form>

                            <h2 class="mt-4">Pagination</h2>
                            <nav>
                                <ul class="pagination">
                                    <li class="page-item disabled">
                                        <a class="page-link" href="#" tabindex="-1">Previous</a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">1</a>
                                    </li>
                                    <li class="page-item active">
                                        <a class="page-link" href="#">2 <span class="visually-hidden">(current)</span></a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">3</a>
                                    </li>
                                    <li class="page-item">
                                        <a class="page-link" href="#">Next</a>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                        <div class="col-md-auto">
                            <h2>Alert</h2>
                            <t t-foreach="bs_theme_colors" t-as="color">
                                <div t-attf-class="alert alert-#{color[0]}">
                                    This is a "<t t-esc="color[1]"/>" alert with a <a href="#" class="alert-link">link</a>.
                                </div>
                            </t>

                            <h2 class="mt-4">Breadcrumb</h2>
                            <nav aria-label="breadcrumb">
                                <ol class="breadcrumb">
                                    <li class="breadcrumb-item"><a href="#">Home</a></li>
                                    <li class="breadcrumb-item"><a href="#">Library</a></li>
                                    <li class="breadcrumb-item active" aria-current="page">Data</li>
                                </ol>
                            </nav>

                            <h2 class="mt-4">Card</h2>
                            <div class="card">
                                <div class="card-header">
                                    Card Header
                                </div>
                                <div class="card-body">
                                    Card Body
                                </div>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item">Item 1</li>
                                    <li class="list-group-item">Item 2</li>
                                </ul>
                                <div class="card-footer">
                                    Card Footer
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <section class="py-2">
                <div class="container">
                    <h1>Utilities &amp; Typography</h1>
                    <div class="row">
                        <div class="col-md">
                            <div class="row g-0">
                                <t t-foreach="odoo_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row g-0 mt-2">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row g-0 mt-2">
                                <t t-foreach="bs_gray_colors" t-as="color">
                                    <div t-attf-class="col-auto bg-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row g-0 mt-4">
                                <t t-foreach="odoo_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row g-0 mt-2">
                                <t t-foreach="bs_theme_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                            <div class="row g-0 mt-2">
                                <t t-foreach="bs_gray_colors" t-as="color">
                                    <div t-attf-class="col-auto text-#{color[0]}">
                                        <div class="py-1 px-3"><t t-esc="color[1]"/></div>
                                    </div>
                                </t>
                            </div>
                        </div>
                        <div class="col-md-auto">
                            <h1>Headings 1</h1>
                            <h2>Headings 2</h2>
                            <h3>Headings 3</h3>
                            <h4>Headings 4</h4>
                            <h5>Headings 5</h5>
                            <h6>Headings 6</h6>
                            <p>Paragraph with <strong>bold</strong>, <span class="text-muted">
muted</span> and <em>italic</em> texts</p>
                            <p><a href="#">Link</a></p>
                            <p><button type="button" class="btn btn-link">Link button</button></p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>
        """
        mismatch_count = 0
        debug_arch = self.env["ir.ui.view"].browse(init["debug_view_id"]).arch_db
        bs_debug_16_0_arch = self._reformat(bs_debug_16_0_arch)
        debug_arch = self._reformat(debug_arch)
        old_max_diff = self.maxDiff
        self.maxDiff = None
        try:
            self.assertEqual(bs_debug_16_0_arch, debug_arch, "BS Debug does not match")
        except AssertionError as e:
            # Collect all mismatches in the log.
            _logger.error(e.args[0])
            mismatch_count += 1

        test_arch = self.env["ir.ui.view"].browse(init["test_view_id"]).arch_db
        updated_chunks = test_arch.split("<!-- Separator -->")[1:-1]
        for expected_chunk, updated_chunk in zip(self._get_chunks(1), updated_chunks):
            expected_chunk = self._reformat(expected_chunk)
            updated_chunk = self._reformat(updated_chunk)
            try:
                self.assertEqual(
                    expected_chunk.replace(r"\n", "").replace(r"&quot;", "'"), updated_chunk, "Chunk should match"
                )
            except AssertionError as e:
                # Collect all mismatches in the log.
                _logger.error(e.args[0])
                mismatch_count += 1
        self.assertEqual(mismatch_count, 0, "All chunks should match")
        self.maxDiff = old_max_diff

        # Check the untouched forked view has been updated to the 16.0 and check
        # that the touched forked view has been converted to BS5.
        generic_view = self.env["ir.ui.view"].browse(init["generic_view_id"])
        touched_specific_view = self.env["ir.ui.view"].browse(init["touched_specific_view_id"])
        untouched_specific_view = self.env["ir.ui.view"].browse(init["untouched_specific_view_id"])
        old_version_dom_part = 'http-equiv="refresh"'
        self.assertTrue(
            old_version_dom_part in init["old_generic_view_arch"],
            "Old arch should contain something that we can trust to be gone in 16.0",
        )
        self.assertFalse(
            old_version_dom_part in generic_view.arch, "The generic view should have been updated to the 16.0 version"
        )
        self.assertTrue(
            old_version_dom_part in touched_specific_view.arch
            and '<div class="oe_structure text-start">' in touched_specific_view.arch,
            "The touched specific view should just have been converted to bootstrap 5",
        )
        self.assertEqual(
            generic_view.arch,
            untouched_specific_view.arch,
            "The untouched specific view should have been updated to the 16.0 version",
        )
