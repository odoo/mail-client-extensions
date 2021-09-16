import * as React from 'react';
import './InfoCell.css';

type InfoCellProps = {
    hrefContent?: string;
    icon: any;
    title: string;
    value: string;
};

const InfoCell = (props: InfoCellProps) => {
    const { hrefContent, icon, title, value } = props;
    if (hrefContent != undefined) {
        return (
            <a className="button-link" href={hrefContent} target="_blank" rel="noreferrer noopener">
                <div className="info-cell">
                    <div>{icon}</div>
                    <div>
                        <div className="info-cell-title">{title}</div>
                        <div className="info-cell-data">{value}</div>
                    </div>
                </div>
            </a>
        );
    } else {
        return (
            <div className="button-link">
                <div className="info-cell">
                    <div>{icon}</div>
                    <div>
                        <div className="info-cell-title">{title}</div>
                        <div className="info-cell-data">{value}</div>
                    </div>
                </div>
            </div>
        );
    }
};

export default InfoCell;
