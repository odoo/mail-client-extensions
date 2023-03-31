function onLogout(state) {
    (0, resetAccessToken)();
    (0, clearTranslationCache)();
    var _a = Partner.enrichPartner(state.email.contactEmail, state.email.contactName),
        partner = _a[0],
        odooUserCompanies = _a[1],
        canCreatePartner = _a[2],
        canCreateProject = _a[3],
        error = _a[4];
    var newState = new State(
        partner,
        canCreatePartner,
        state.email,
        odooUserCompanies,
        null,
        null,
        canCreateProject,
        error,
    );
    return (0, pushToRoot)((0, buildView)(newState));
}
function buildCardActionsView(state, card) {
    var canContactOdooDatabase = state.error.canContactOdooDatabase && State.isLogged;
    if (State.isLogged) {
        card.addCardAction(
            CardService.newCardAction()
                .setText((0, _t)("Logout"))
                .setOnClickAction((0, actionCall)(state, "onLogout")),
        );
    }
    card.addCardAction(
        CardService.newCardAction()
            .setText((0, _t)("Debug"))
            .setOnClickAction((0, actionCall)(state, "buildDebugView")),
    );
}
