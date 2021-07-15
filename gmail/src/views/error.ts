import { State } from "../models/state";
import { createKeyValueWidget, actionCall } from "./helpers";
import { buildView } from "./index";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { _t } from "../services/translation";

function onCloseError(state: State) {
    state.error.code = null;
    return updateCard(buildView(state));
}

function _addError(message: string, state: State, icon: string = null): CardSection {
    const errorSection = CardService.newCardSection();

    errorSection.addWidget(
        createKeyValueWidget(
            null,
            message,
            icon,
            null,
            CardService.newImageButton()
                .setAltText(_t("Close"))
                .setIconUrl(UI_ICONS.close)
                .setOnClickAction(actionCall(state, "onCloseError")),
        ),
    );
    return errorSection;
}

export function buildErrorView(state: State, card: Card) {
    const error = state.error;

    const ignoredErrors = ["company_created", "company_updated"];
    if (ignoredErrors.indexOf(error.code) >= 0) {
        return;
    }

    if (error.code === "http_error_odoo") {
        const errorSection = _addError(error.message, state);
        errorSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Login"))
                .setOnClickAction(CardService.newAction().setFunctionName("buildLoginMainView")),
        );
        card.addSection(errorSection);
    } else if (error.code === "insufficient_credit") {
        const errorSection = _addError(error.message, state);
        errorSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Buy new credits"))
                .setOpenLink(CardService.newOpenLink().setUrl(error.information)),
        );
        card.addSection(errorSection);
    } else if (error.code === "missing_data") {
        card.addSection(_addError(error.message, state));
    } else {
        let errors = [error.message, error.information].filter((x) => x);
        const errorMessage = errors.join("\n");
        card.addSection(_addError(errorMessage, state));
    }
}
