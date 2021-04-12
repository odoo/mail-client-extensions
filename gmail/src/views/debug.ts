import { createKeyValueWidget } from "./helpers";
import { State } from "../models/state";
import { _t, clearTranslationCache } from "../services/translation";

export function buildDebugView() {
    const card = CardService.newCardBuilder();

    card.setHeader(
        CardService.newCardHeader().setTitle(_t("Debug Zone")).setSubtitle(_t("Debug zone for development purpose.")),
    );

    card.addSection(
        CardService.newCardSection().addWidget(createKeyValueWidget(_t("Odoo Server URL"), State.odooServerUrl)),
    );

    card.addSection(
        CardService.newCardSection().addWidget(createKeyValueWidget(_t("Odoo Access Token"), State.accessToken)),
    );

    card.addSection(
        CardService.newCardSection().addWidget(
            CardService.newTextButton()
                .setText(_t("Clear Translations Cache"))
                .setOnClickAction(CardService.newAction().setFunctionName("clearTranslationCache")),
        ),
    );

    return card.build();
}
