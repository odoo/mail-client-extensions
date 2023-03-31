var __assign =
    (this && this.__assign) ||
    function () {
        __assign =
            Object.assign ||
            function (t) {
                for (var s, i = 1, n = arguments.length; i < n; i++) {
                    s = arguments[i];
                    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
                }
                return t;
            };
        return __assign.apply(this, arguments);
    };
/**
 * Object which contains all data for the application.
 *
 * In App-Script, all event handler are function and not method. We can only pass string
 * as arguments. So this object is serialized, then given to the event handler and then
 * unserialize to retrieve the original object.
 *
 * That's how we manage the state of the application without performing a big amount of
 * read / write in the cache.
 */
var State = /** @class */ (function () {
    function State(
        partner,
        canCreatePartner,
        email,
        odooUserCompanies,
        partners,
        searchedProjects,
        canCreateProject,
        error,
    ) {
        this.partner = partner;
        this.canCreatePartner = canCreatePartner;
        this.email = email;
        this.odooUserCompanies = odooUserCompanies;
        this.searchedPartners = partners;
        this.searchedProjects = searchedProjects;
        this.canCreateProject = canCreateProject;
        this.error = error;
    }
    State.prototype.toJson = function () {
        return JSON.stringify(this);
    };
    /**
     * Unserialize the state object (reverse JSON.stringify).
     */
    State.fromJson = function (json) {
        var values = JSON.parse(json);
        var partnerValues = values.partner || {};
        var canCreatePartner = values.canCreatePartner;
        var emailValues = values.email || {};
        var errorValues = values.error || {};
        var partnersValues = values.searchedPartners;
        var projectsValues = values.searchedProjects;
        var canCreateProject = values.canCreateProject;
        var partner = Partner.fromJson(partnerValues);
        var email = Email.fromJson(emailValues);
        var error = ErrorMessage.fromJson(errorValues);
        var odooUserCompanies = values.odooUserCompanies;
        var searchedPartners = partnersValues
            ? partnersValues.map(function (partnerValues) {
                  return Partner.fromJson(partnerValues);
              })
            : null;
        var searchedProjects = projectsValues
            ? projectsValues.map(function (projectValues) {
                  return Project.fromJson(projectValues);
              })
            : null;
        // "isCompanyDescriptionUnfolded" is not copied
        // to re-fold the description if we go back / refresh
        return new State(
            partner,
            canCreatePartner,
            email,
            odooUserCompanies,
            searchedPartners,
            searchedProjects,
            canCreateProject,
            error,
        );
    };
    Object.defineProperty(State.prototype, "odooCompaniesParameter", {
        /**
         * Return the companies of the Odoo user as a GET parameter to add in a URL or an
         * empty string if the information is missing.
         *
         * e.g.
         *     &cids=1,3,7
         */
        get: function () {
            if (this.odooUserCompanies && this.odooUserCompanies.length) {
                var cids = this.odooUserCompanies.sort().join(",");
                return "&cids=".concat(cids);
            }
            return "";
        },
        enumerable: false,
        configurable: true,
    });
    Object.defineProperty(State, "accessToken", {
        /**
         * Cache / user properties management.
         *
         * Introduced with static getter / setter because they are shared between all the
         * application cards.
         */
        get: function () {
            var accessToken = (0, getAccessToken)();
            return (0, isTrue)(accessToken);
        },
        enumerable: false,
        configurable: true,
    });
    Object.defineProperty(State, "isLogged", {
        get: function () {
            return !!this.accessToken;
        },
        enumerable: false,
        configurable: true,
    });
    Object.defineProperty(State, "odooLoginUrl", {
        /**
         * Return the URL require to login to the Odoo database.
         */
        get: function () {
            var loginUrl = (0, getOdooAuthUrl)();
            return (0, isTrue)(loginUrl);
        },
        enumerable: false,
        configurable: true,
    });
    Object.defineProperty(State, "odooServerUrl", {
        /**
         * Return the base URL of the Odoo database.
         */
        get: function () {
            var userProperties = PropertiesService.getUserProperties();
            var serverUrl = userProperties.getProperty("ODOO_SERVER_URL");
            return (0, isTrue)(serverUrl);
        },
        /**
         * Change the base URL of the Odoo database.
         */
        set: function (value) {
            var userProperties = PropertiesService.getUserProperties();
            userProperties.setProperty("ODOO_SERVER_URL", value);
        },
        enumerable: false,
        configurable: true,
    });
    Object.defineProperty(State, "odooSharedSecret", {
        /**
         * Return the shared secret between the add-on and IAP
         * (which is used to authenticate the add-on to IAP).
         */
        get: function () {
            var scriptProperties = PropertiesService.getScriptProperties();
            var sharedSecret = scriptProperties.getProperty("ODOO_SHARED_SECRET");
            return (0, isTrue)(sharedSecret);
        },
        enumerable: false,
        configurable: true,
    });
    /**
     * Dictionary which inform us on which record we already logged the email.
     * So the user can not log 2 times the same email on the same record.
     * This is stored into the cache, so we don't need to modify the Odoo models.
     *
     * Note: the cache expire after 6 hours.
     *
     * Returns:
     *     {
     *         "partners": [3, 6], // email already logged on the partner 3 and 6
     *         "leads": [7, 14],
     *     }
     */
    State.getLoggingState = function (messageId) {
        var cache = CacheService.getUserCache();
        var loggingStateStr = cache.get("ODOO_LOGGING_STATE_" + this.odooServerUrl + "_" + messageId);
        var defaultValues = {
            partners: [],
            leads: [],
            tickets: [],
            tasks: [],
        };
        if (!loggingStateStr || !loggingStateStr.length) {
            return defaultValues;
        }
        return __assign(__assign({}, defaultValues), JSON.parse(loggingStateStr));
    };
    /**
     * Save the fact that we logged the email on the record, in the cache.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    State.setLoggingState = function (messageId, res_model, res_id) {
        var loggingState = this.getLoggingState(messageId);
        if (loggingState[res_model].indexOf(res_id) < 0) {
            loggingState[res_model].push(res_id);
            var cache = CacheService.getUserCache();
            // The cache key depend on the current email open and on the Odoo database
            var cacheKey = "ODOO_LOGGING_STATE_" + this.odooServerUrl + "_" + messageId;
            cache.put(cacheKey, JSON.stringify(loggingState), 21600);
            return true;
        }
        return false;
    };
    /**
     * Check if the email has not been logged on the record.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    State.checkLoggingState = function (messageId, res_model, res_id) {
        var loggingState = this.getLoggingState(messageId);
        return loggingState[res_model].indexOf(res_id) < 0;
    };
    return State;
})();
