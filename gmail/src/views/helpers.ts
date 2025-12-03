import { UI_ICONS } from "./icons";
import { State } from "../models/state";
import { escapeHtml } from "../utils/html";
import { truncate } from "../utils/format";

/**
 * Remove all cards and push the new one
 */
export function pushToRoot(card: Card) {
    return CardService.newNavigation().popToRoot().updateCard(card);
}

/**
 * Remove the last card and push a new one.
 */
export function updateCard(card: Card) {
    return CardService.newNavigation().updateCard(card);
}

/**
 * Push a new card on the stack.
 */
export function pushCard(card: Card) {
    return CardService.newNavigation().pushCard(card);
}

/**
 * Build a widget "Key / Value / Icon"
 *
 * If the icon is not a valid URL, take the icon from:
 * https://github.com/webdog/octicons-png
 */
export function createKeyValueWidget(
    label: string,
    content: string,
    icon: string = null,
    bottomLabel: string = null,
    button: Button = null,
    action: any = null,
    wrap: boolean = true,
    iconLabel: string = null,
    iconCropStyle: GoogleAppsScript.Card_Service.ImageCropType = CardService.ImageCropType.SQUARE,
) {
    const widget = CardService.newDecoratedText().setText(content);
    if (label && label.length) {
        widget.setTopLabel(escapeHtml(label));
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
        const isIconUrl =
            icon.indexOf("http://") === 0 ||
            icon.indexOf("https://") === 0 ||
            icon.indexOf("data:image/") === 0;
        if (!isIconUrl) {
            throw new Error("Invalid icon URL");
        }

        widget.setStartIcon(
            CardService.newIconImage()
                .setIconUrl(icon)
                .setImageCropType(iconCropStyle)
                .setAltText(escapeHtml(iconLabel || label)),
        );
    }

    widget.setWrapText(wrap);

    return widget;
}

function _handleActionCall(event) {
    const functionName = event.parameters.functionName;
    const parameters = JSON.parse(event.parameters.parameters);
    if (!/^on[A-Z][a-zA-Z]+(\$[0-9]+)?$/.test(functionName)) {
        throw new Error("Invalid function name");
    }
    // @ts-ignore
    const toCall = this[functionName];
    if (event.parameters.state?.length) {
        const state = State.fromJson(event.parameters.state);
        return toCall(state, parameters, event.formInput);
    }
    return toCall(parameters, event.formInput);
}

/**
 * Create an action which will call the given function and pass the state in arguments.
 *
 * This is necessary because event handlers can call only function and all arguments
 * must be strings. Therefor we serialized the state and other arguments to clean the code
 * and to be able to access to it in the event handlers.
 */
export function actionCall(state: State | null, functionName: string, parameters: any = {}) {
    return CardService.newAction()
        .setFunctionName(_handleActionCall.name)
        .setParameters({
            functionName: functionName,
            state: state ? state.toJson() : "",
            parameters: JSON.stringify(parameters),
        });
}

export function notify(message: string) {
    return CardService.newActionResponseBuilder()
        .setNotification(CardService.newNotification().setText(message))
        .build();
}

export function openUrl(url: string) {
    return CardService.newActionResponseBuilder()
        .setOpenLink(CardService.newOpenLink().setUrl(url))
        .build();
}
