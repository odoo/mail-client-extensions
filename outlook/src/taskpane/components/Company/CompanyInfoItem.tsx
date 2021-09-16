import * as React from 'react';
import { IconDefinition } from '@fortawesome/fontawesome-common-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import InfoCell from '../InfoCell/InfoCell';

type CompanyInfoItemProps = {
    icon: IconDefinition;
    title: string;
    value: string;
    hrefContent?: string;
};

const CompanyInfoItem = (props: CompanyInfoItemProps) => {
    const icon = (
        <div className="company-info-icon">
            <FontAwesomeIcon icon={props.icon} color="darkgrey" className="fa-fw" />
        </div>
    );

    let infoCell;

    if (props.hrefContent == undefined) {
        infoCell = <InfoCell icon={icon} title={props.title} value={props.value} />;
    } else {
        infoCell = <InfoCell hrefContent={props.hrefContent} icon={icon} title={props.title} value={props.value} />;
    }

    return <div className="company-info-item">{infoCell}</div>;
};

export default CompanyInfoItem;
