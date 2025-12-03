import { createKeyValueWidget } from "./helpers";
import { _t, clearTranslationCache } from "../services/translation";
import { getAccessToken } from "src/services/odoo_auth";
import { getOdooServerUrl } from "src/services/app_properties";

export function onBuildDebugView() {
    const card = CardService.newCardBuilder();
    const odooServerUrl = getOdooServerUrl();
    const odooAccessToken = getAccessToken();

    card.setHeader(
        CardService.newCardHeader()
            .setTitle(_t("Debug Zone"))
            .setSubtitle(_t("Debug zone for development purpose.")),
    );

    card.addSection(
        CardService.newCardSection().addWidget(
            createKeyValueWidget(_t("Odoo Server URL"), odooServerUrl),
        ),
    );

    card.addSection(
        CardService.newCardSection().addWidget(
            createKeyValueWidget(_t("Odoo Access Token"), odooAccessToken),
        ),
    );

    card.addSection(
        CardService.newCardSection().addWidget(
            CardService.newTextButton()
                .setText(_t("Clear Translations Cache"))
                .setOnClickAction(
                    CardService.newAction().setFunctionName(clearTranslationCache.name),
                ),
        ),
    );

    return card.build();
}
