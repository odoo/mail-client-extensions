function onCloseError(state) {
    state.error.code = null;
    return (0, updateCard)((0, buildView)(state));
}
function _addError(message, state, icon) {
    if (icon === void 0) {
        icon = null;
    }
    var errorSection = CardService.newCardSection();
    errorSection.addWidget(
        (0, createKeyValueWidget)(
            null,
            message,
            icon,
            null,
            CardService.newImageButton()
                .setAltText((0, _t)("Close"))
                .setIconUrl(UI_ICONS.close)
                .setOnClickAction((0, actionCall)(state, "onCloseError")),
        ),
    );
    return errorSection;
}
function buildErrorView(state, card) {
    var error = state.error;
    var ignoredErrors = ["company_created", "company_updated"];
    if (ignoredErrors.indexOf(error.code) >= 0) {
        return;
    }
    if (error.code === "http_error_odoo") {
        var errorSection = _addError(error.message, state);
        errorSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Login"))
                .setOnClickAction(CardService.newAction().setFunctionName("buildLoginMainView")),
        );
        card.addSection(errorSection);
    } else if (error.code === "insufficient_credit") {
        var errorSection = _addError(error.message, state);
        errorSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Buy new credits"))
                .setOpenLink(CardService.newOpenLink().setUrl(error.information)),
        );
        card.addSection(errorSection);
    } else if (error.code === "missing_data") {
        card.addSection(_addError(error.message, state));
    } else {
        var errors = [error.message, error.information].filter(function (x) {
            return x;
        });
        var errorMessage = errors.join("\n");
        card.addSection(_addError(errorMessage, state));
    }
}
