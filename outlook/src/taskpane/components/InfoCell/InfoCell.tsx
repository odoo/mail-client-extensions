import * as React from "react";
import { FontIcon } from 'office-ui-fabric-react/lib/Icon';

import "./InfoCell.css";

type InfoCellProps = {
    hrefContent: string,
    iconName: string,
    iconClassName: string,
    title: string,
    value: string
};
type InfoCellState = {};

class InfoCell extends React.Component<InfoCellProps, InfoCellState> {
    constructor(props, context) {
        super(props, context);
    }

    render() {
        const {hrefContent, iconName, iconClassName, title, value} = this.props;
        return <a className="button-link" href={hrefContent} target="_blank" rel="noreferrer noopener">
            <div className="info-cell">
                <div className="info-cell-left">
                <FontIcon iconName={iconName} className={iconClassName}/>
                </div>
                <div className="info-cell-right">
                <div className="info-cell-title">{title}</div>
                <div className="info-cell-value">{value}</div>
                </div>
            </div>
        </a>
    }
}
export default InfoCell;
