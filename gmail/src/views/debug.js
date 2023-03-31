function buildDebugView() {
    var card = CardService.newCardBuilder();
    card.setHeader(
        CardService.newCardHeader()
            .setTitle((0, _t)("Debug Zone"))
            .setSubtitle((0, _t)("Debug zone for development purpose.")),
    );
    card.addSection(
        CardService.newCardSection().addWidget(
            (0, createKeyValueWidget)((0, _t)("Odoo Server URL"), State.odooServerUrl),
        ),
    );
    card.addSection(
        CardService.newCardSection().addWidget(
            (0, createKeyValueWidget)((0, _t)("Odoo Access Token"), State.accessToken),
        ),
    );
    card.addSection(
        CardService.newCardSection().addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Clear Translations Cache"))
                .setOnClickAction(CardService.newAction().setFunctionName("clearTranslationCache")),
        ),
    );
    return card.build();
}
