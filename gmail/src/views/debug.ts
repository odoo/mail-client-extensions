import { createKeyValueWidget } from "./helpers";
import { State } from "../models/state";

export function buildDebugView() {
    const card = CardService.newCardBuilder();

    card.setHeader(
        CardService.newCardHeader().setTitle("Debug Zone").setSubtitle("Debug zone for development purpose."),
    );

    card.addSection(
        CardService.newCardSection().addWidget(createKeyValueWidget("Odoo Server URL", State.odooServerUrl)),
    );

    card.addSection(
        CardService.newCardSection().addWidget(createKeyValueWidget("Odoo Access Token", State.accessToken)),
    );

    return card.build();
}
