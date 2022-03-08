import * as React from 'react';

function CompanySocialIcons({ twitter, facebook, linkedin, crunchbase }) {
    return (
        <div className="social-links" onClick={(e) => e.stopPropagation()}>
            {twitter && (
                <a href={'https://twitter.com/' + twitter} target="_blank" rel="noreferrer noopener">
                    <img src="assets/social/twitter.ico" />
                </a>
            )}
            {facebook && (
                <a href={'https://facebook.com/' + facebook} target="_blank" rel="noreferrer noopener">
                    <img src="assets/social/facebook.ico" />
                </a>
            )}
            {linkedin && (
                <a href={'https://linkedin.com/' + linkedin} target="_blank" rel="noreferrer noopener">
                    <img src="assets/social/linkedin.ico" />
                </a>
            )}
            {crunchbase && (
                <a href={'https://crunchbase.com/' + crunchbase} target="_blank" rel="noreferrer noopener">
                    <img src="assets/social/crunchbase.ico" />
                </a>
            )}
        </div>
    );
}

export default CompanySocialIcons;
