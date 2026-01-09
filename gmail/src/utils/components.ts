import { HOST } from "../consts";
import { ActionCall, OpenLink } from "./actions";

/**
 * Build the JSON format of the components to construct the view.
 *
 * https://addons.gsuite.google.com/uikit/builder
 * https://gw-card-builder.web.app/
 *
 * https://developers.google.com/workspace/add-ons/guides/alternate-runtimes
 */
abstract class Component {
    abstract build();
}

export class CardSection {
    header: string;
    widgets: Component[];

    constructor(widgets?: Component[]) {
        this.header = "";
        this.widgets = widgets || [];
    }

    setHeader(header: string) {
        this.header = header;
    }

    addWidget(widget: Component) {
        this.widgets.push(widget);
    }

    build() {
        const ret = {
            widgets: this.widgets.map((w) => w.build()),
        };
        if (this.header?.length) {
            ret["header"] = this.header;
        }
        return ret;
    }
}

export class Card {
    sections: CardSection[];
    actions: [string, ActionCall][]; // actions shown in the kebab menu

    constructor(sections?: CardSection[]) {
        this.sections = sections || [];
        this.actions = [];
    }

    addSection(section: CardSection) {
        this.sections.push(section);
    }

    addAction(label: string, action: ActionCall) {
        this.actions.push([label, action]);
    }

    build() {
        const ret = {
            sections: this.sections.map((s) => s.build()),
        };
        if (this.actions.length) {
            ret["cardActions"] = this.actions.map(([label, action]) => ({
                actionLabel: label,
                onClick: action.build(),
            }));
        }
        return ret;
    }
}

export class TextParagraph extends Component {
    text: string;
    constructor(text: string) {
        super();
        this.text = text;
    }
    build() {
        return {
            textParagraph: {
                text: this.text,
            },
        };
    }
}

export class Button extends Component {
    text: string;
    onClick: ActionCall | OpenLink;
    disabled: boolean;
    icon?: string;
    iconLabel?: string;
    iconCropStyle: ImageCropType;
    color?: string;
    borderless: boolean;

    constructor(
        text: string,
        onClick: ActionCall | OpenLink,
        color?: string,
        disabled: boolean = false,
        icon?: string,
        iconLabel?: string,
        iconCropStyle: ImageCropType = ImageCropType.CIRCLE,
        borderless: boolean = false,
    ) {
        super();
        if (icon?.length && icon.startsWith("/")) {
            // Relative URL
            icon = `${HOST}${icon}`;
        }
        this.text = text;
        this.onClick = onClick;
        this.disabled = disabled;
        this.icon = icon;
        this.iconLabel = iconLabel;
        this.iconCropStyle = iconCropStyle;
        this.color = color;
        this.borderless = borderless;
    }

    build() {
        const buttonValues = {
            text: this.text,
            onClick: this.onClick.build(),
            disabled: this.disabled,
        };
        if (this.icon) {
            buttonValues["icon"] = {
                iconUrl: this.icon,
                altText: this.iconLabel,
                imageType: this.iconCropStyle,
            };
        }
        if (this.color) {
            // Gmail expect the color converted to RGB, each value
            // is between 0 and 1
            buttonValues["color"] = {
                red: parseInt(this.color.slice(1, 3), 16) / 256,
                green: parseInt(this.color.slice(3, 5), 16) / 256,
                blue: parseInt(this.color.slice(5, 7), 16) / 256,
            };
        }
        if (this.borderless) {
            buttonValues["color"] = {
                red: 1,
                green: 1,
                blue: 1,
                alpha: 1,
            };
        }
        return { buttonList: { buttons: [buttonValues] } };
    }
}

export class LinkButton extends Component {
    text: string;
    onClick: ActionCall | OpenLink;

    constructor(text: string, onClick: ActionCall | OpenLink) {
        super();
        this.text = text;
        this.onClick = onClick;
    }

    build() {
        return {
            decoratedText: {
                text: `<font color=\"#13A7A4\">${this.text}</font></b>`,
                onClick: this.onClick.build(),
            },
        };
    }
}

/**
 * Helper user to build icon button.
 */
export class IconButton extends Button {
    constructor(
        onClick: ActionCall | OpenLink,
        icon?: string,
        iconLabel?: string,
        iconCropStyle: ImageCropType = ImageCropType.CIRCLE,
    ) {
        super(undefined, onClick, undefined, false, icon, iconLabel, iconCropStyle);
    }
}

/**
 * Show many buttons in the same line.
 */
export class ButtonsList extends Component {
    buttons: Button[];

    constructor(buttons: Button[] = []) {
        super();
        this.buttons = buttons;
    }

    addButton(button: Button) {
        this.buttons.push(button);
    }

    build() {
        return {
            buttonList: { buttons: this.buttons.map((b) => b.build().buttonList.buttons[0]) },
        };
    }
}

export enum ImageCropType {
    SQUARE = "SQUARE",
    CIRCLE = "CIRCLE",
}

export class DecoratedText extends Component {
    label: string;
    content: string;
    icon?: string;
    bottomLabel?: string;
    button?: Button;
    onClick?: ActionCall | OpenLink;
    wrap: boolean;
    iconLabel?: string;
    iconCropStyle: ImageCropType;

    constructor(
        label: string,
        content: string,
        icon: string = undefined,
        bottomLabel: string = undefined,
        button: Button = undefined,
        onClick: ActionCall | OpenLink = undefined,
        wrap: boolean = true,
        iconLabel: string = undefined,
        iconCropStyle: ImageCropType = ImageCropType.CIRCLE,
    ) {
        super();
        if (icon?.length && icon.startsWith("/")) {
            // Relative URL
            icon = `${HOST}${icon}`;
        }

        this.label = label;
        this.content = content;
        this.bottomLabel = bottomLabel;
        this.button = button;
        this.onClick = onClick;
        this.wrap = wrap;
        this.icon = icon;
        this.iconLabel = iconLabel;
        this.iconCropStyle = iconCropStyle;
    }
    build() {
        const ret = {
            decoratedText: {
                text: this.content,
                wrapText: this.wrap,
            },
        };
        if (this.button) {
            ret.decoratedText["button"] = this.button.build().buttonList.buttons[0];
        }
        if (this.icon) {
            ret.decoratedText["icon"] = {
                iconUrl: this.icon,
                altText: this.iconLabel,
                imageType: this.iconCropStyle,
            };
        }
        if (this.label) {
            ret.decoratedText["topLabel"] = this.label;
        }
        if (this.bottomLabel) {
            ret.decoratedText["bottomLabel"] = this.bottomLabel;
        }
        if (this.onClick) {
            ret.decoratedText["onClick"] = this.onClick.build();
        }
        return ret;
    }
}

export class Image extends Component {
    url: string;
    altText?: string;
    onClick?: ActionCall | OpenLink;

    constructor(url: string, altText?: string, onClick?: ActionCall | OpenLink) {
        super();
        if (url.startsWith("/")) {
            // Relative URL
            url = `${HOST}${url}`;
        }
        this.url = url;
        this.altText = altText;
        this.onClick = onClick;
    }
    build() {
        const ret = { image: { imageUrl: this.url } };
        if (this.altText) {
            ret.image["altText"] = this.altText;
        }
        if (this.onClick) {
            ret.image["onClick"] = this.onClick.build();
        }
        return ret;
    }
}

export class TextInput extends Component {
    name: string;
    label: string;
    onChange?: ActionCall;
    placeholder?: string;
    value?: string;

    constructor(
        name: string,
        label: string,
        onChange?: ActionCall,
        placeholder?: string,
        value?: string,
    ) {
        super();
        this.name = name;
        this.label = label;
        this.onChange = onChange;
        this.placeholder = placeholder;
        this.value = value;
    }
    build() {
        const ret = {
            textInput: {
                name: this.name,
                label: this.label,
            },
        };
        if (this.onChange) {
            ret.textInput["onChangeAction"] = this.onChange.build()["action"];
        }
        if (this.placeholder) {
            ret.textInput["hintText"] = this.placeholder;
        }
        if (this.value) {
            ret.textInput["value"] = this.value;
        }
        return ret;
    }
}
