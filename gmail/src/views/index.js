function buildView(state) {
    var card = CardService.newCardBuilder();
    if (state.error.code) {
        (0, buildErrorView)(state, card);
    }
    (0, buildPartnerView)(state, card);
    (0, buildCompanyView)(state, card);
    (0, buildCardActionsView)(state, card);
    if (!State.isLogged) {
        card.setFixedFooter(
            CardService.newFixedFooter().setPrimaryButton(
                CardService.newTextButton()
                    .setText((0, _t)("Login"))
                    .setBackgroundColor("#00A09D")
                    .setOnClickAction((0, actionCall)(state, "buildLoginMainView")),
            ),
        );
    }
    return card.build();
}
