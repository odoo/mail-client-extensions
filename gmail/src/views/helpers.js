/**
 * Remove all cards and push the new one
 */
function pushToRoot(card) {
    return CardService.newNavigation().popToRoot().updateCard(card);
}
/**
 * Remove the last card and push a new one.
 */
function updateCard(card) {
    return CardService.newNavigation().updateCard(card);
}
/**
 * Push a new card on the stack.
 */
function pushCard(card) {
    return CardService.newNavigation().pushCard(card);
}
/**
 * Build a widget "Key / Value / Icon"
 *
 * If the icon if not a valid URL, take the icon from:
 * https://github.com/webdog/octicons-png
 */
function createKeyValueWidget(label, content, icon, bottomLabel, button, action, wrap, iconLabel, iconCropStyle) {
    if (icon === void 0) {
        icon = null;
    }
    if (bottomLabel === void 0) {
        bottomLabel = null;
    }
    if (button === void 0) {
        button = null;
    }
    if (action === void 0) {
        action = null;
    }
    if (wrap === void 0) {
        wrap = true;
    }
    if (iconLabel === void 0) {
        iconLabel = null;
    }
    if (iconCropStyle === void 0) {
        iconCropStyle = CardService.ImageCropType.SQUARE;
    }
    var widget = CardService.newDecoratedText().setText(content).setWrapText(true);
    if (label && label.length) {
        widget.setTopLabel((0, escapeHtml)(label));
    }
    if (bottomLabel) {
        widget.setBottomLabel(bottomLabel);
    }
    if (button) {
        widget.setButton(button);
    }
    if (action) {
        if (typeof action === "string") {
            widget.setOpenLink(CardService.newOpenLink().setUrl(action));
        } else {
            widget.setOnClickAction(action);
        }
    }
    if (icon && icon.length) {
        var isIconUrl =
            icon.indexOf("http://") === 0 || icon.indexOf("https://") === 0 || icon.indexOf("data:image/") === 0;
        if (!isIconUrl) {
            throw new Error("Invalid icon URL");
        }
        widget.setStartIcon(
            CardService.newIconImage()
                .setIconUrl(icon)
                .setImageCropType(iconCropStyle)
                .setAltText((0, escapeHtml)(iconLabel || label)),
        );
    }
    widget.setWrapText(wrap);
    return widget;
}
function _handleActionCall(event) {
    var functionName = event.parameters.functionName;
    var state = State.fromJson(event.parameters.state);
    var parameters = JSON.parse(event.parameters.parameters);
    var inputs = event.formInputs;
    return eval(functionName)(state, parameters, inputs);
}
/**
 * Create an action which will call the given function and pass the state in arguments.
 *
 * This is necessary because event handlers can call only function and all arguments
 * must be strings. Therefor we serialized the state and other arguments to clean the code
 * and to be able to access to it in the event handlers.
 */
function actionCall(state, functionName, parameters) {
    if (parameters === void 0) {
        parameters = {};
    }
    return CardService.newAction()
        .setFunctionName("_handleActionCall")
        .setParameters({
            functionName: functionName,
            state: state.toJson(),
            parameters: JSON.stringify(parameters),
        });
}
function notify(message) {
    return CardService.newActionResponseBuilder()
        .setNotification(CardService.newNotification().setText(message))
        .build();
}
function openUrl(url) {
    return CardService.newActionResponseBuilder().setOpenLink(CardService.newOpenLink().setUrl(url)).build();
}
