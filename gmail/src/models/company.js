var Company = /** @class */ (function () {
    function Company() {}
    /**
     * Parse the dictionary returned by IAP.
     */
    Company.fromIapResponse = function (values) {
        var company = new Company();
        company.name = (0, isTrue)(values.name);
        company.email = (0, first)(values.email);
        company.phone = (0, first)(values.phone_numbers);
        company.isEnriched = !!Object.keys(values).length;
        company.emails = (0, isTrue)(values.email) ? values.email.join("\n") : null;
        company.phones = (0, isTrue)(values.phone_numbers) ? values.phone_numbers.join("\n") : null;
        company.image = (0, isTrue)(values.logo);
        company.website = (0, formatUrl)(values.domain);
        company.description = (0, isTrue)(values.description);
        company.address = (0, isTrue)(values.location);
        // Social Medias
        company.facebook = (0, isTrue)(values.facebook);
        company.twitter = (0, isTrue)(values.twitter);
        company.linkedin = (0, isTrue)(values.linkedin);
        company.crunchbase = (0, isTrue)(values.crunchbase);
        // Additional Information
        company.employees = values.employees || null;
        company.annualRevenue = (0, isTrue)(values.estimated_annual_revenue);
        company.industry = (0, isTrue)(values.industry);
        company.twitterBio = (0, isTrue)(values.twitter_bio);
        company.twitterFollowers = values.twitter_followers || null;
        company.foundedYear = values.founded_year;
        company.timezone = (0, isTrue)(values.timezone);
        company.timezoneUrl = (0, isTrue)(values.timezone_url);
        company.tags = (0, isTrue)(values.tag) ? values.tag.join(", ") : null;
        company.companyType = (0, isTrue)(values.company_type);
        return company;
    };
    /**
     * Unserialize the company object (reverse JSON.stringify).
     */
    Company.fromJson = function (values) {
        var company = new Company();
        company.id = values.id;
        company.name = values.name;
        company.email = values.email;
        company.phone = values.phone;
        company.address = values.address;
        company.annualRevenue = values.annualRevenue;
        company.companyType = values.companyType;
        company.description = values.description;
        company.emails = values.emails;
        company.employees = values.employees;
        company.foundedYear = values.foundedYear;
        company.image = values.image;
        company.industry = values.industry;
        company.mobile = values.mobile;
        company.phones = values.phones;
        company.tags = values.tags;
        company.timezone = values.timezone;
        company.timezoneUrl = values.timezoneUrl;
        company.twitterBio = values.twitterBio;
        company.twitterFollowers = values.twitterFollowers;
        company.website = values.website;
        company.crunchbase = values.crunchbase;
        company.facebook = values.facebook;
        company.twitter = values.twitter;
        company.linkedin = values.linkedin;
        return company;
    };
    /**
     * Parse the dictionary returned by an Odoo database.
     */
    Company.fromOdooResponse = function (values) {
        if (!values.id || values.id < 0) {
            return null;
        }
        var iapInfo = values.additionalInfo || {};
        var company = this.fromIapResponse(iapInfo);
        // Overwrite IAP information with the Odoo client database information
        company.id = values.id;
        company.name = values.name;
        company.email = values.email;
        company.phone = values.phone;
        company.mobile = values.mobile;
        company.website = values.website;
        company.image = values.image ? "data:image/png;base64," + values.image : null;
        if (values.address) {
            company.address = "";
            if ((0, isTrue)(values.address.street)) {
                company.address += values.address.street + ", ";
            }
            if ((0, isTrue)(values.address.zip)) {
                company.address += values.address.zip + " ";
            }
            if ((0, isTrue)(values.address.city)) {
                company.address += values.address.city + " ";
            }
            if ((0, isTrue)(values.address.country)) {
                company.address += values.address.country;
            }
        }
        return company;
    };
    return Company;
})();
