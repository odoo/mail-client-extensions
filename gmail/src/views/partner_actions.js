function onSearchPartner(state) {
    if (!state.searchedPartners) {
        var _a = Partner.searchPartner(state.partner.email),
            partners = _a[0],
            error = _a[1];
        state.searchedPartners = partners;
    }
    return (0, buildSearchPartnerView)(state, state.partner.email, true);
}
function onReloadPartner(state) {
    var _a;
    (_a = Partner.getPartner(state.partner.email, state.partner.name, state.partner.id)),
        (state.partner = _a[0]),
        (state.odooUserCompanies = _a[1]),
        (state.canCreatePartner = _a[2]),
        (state.canCreateProject = _a[3]),
        (state.error = _a[4]);
    return (0, updateCard)((0, buildView)(state));
}
function buildPartnerActionView(state, partnerSection) {
    var isLogged = State.isLogged;
    var canContactOdooDatabase = state.error.canContactOdooDatabase && isLogged;
    if (canContactOdooDatabase) {
        var actionButtonSet = CardService.newButtonSet();
        if (state.partner.id) {
            actionButtonSet.addButton(
                CardService.newImageButton()
                    .setAltText((0, _t)("Refresh"))
                    .setIconUrl(UI_ICONS.reload)
                    .setOnClickAction((0, actionCall)(state, "onReloadPartner")),
            );
        }
        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText((0, _t)("Search contact"))
                .setIconUrl(UI_ICONS.search)
                .setOnClickAction((0, actionCall)(state, "onSearchPartner")),
        );
        partnerSection.addWidget(actionButtonSet);
    } else if (!isLogged) {
        // add button but it redirects to the login page
        var actionButtonSet = CardService.newButtonSet();
        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText((0, _t)("Search contact"))
                .setIconUrl(UI_ICONS.search)
                .setOnClickAction((0, actionCall)(state, "buildLoginMainView")),
        );
        partnerSection.addWidget(actionButtonSet);
    }
}
