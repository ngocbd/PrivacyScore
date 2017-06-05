from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from privacyscore.evaluation.description import describe_locations
from privacyscore.evaluation.rating import Rating


# TODO: Cleaner solution? Inline lambdas are ugly and not flexible at all.

# Checks are ordered in groups.
# Each check defines a set of keys it takes, the rating function
# and how to rate it (or not to rate it with None) when at least one key is
# missing.

CHECKS = {
    'general': OrderedDict(),
    'privacy': OrderedDict(),
    'ssl': OrderedDict(),
}
# Check for presence of cookies (first or third party)
# 0 cookies: good
# else: bad
# TODO This may be a bit brutal - not all cookies are terrible
# DH: This is a legacy check that shold be replaced by a series
# of checks that pull data out from Max's new fance cookie dictionary
# we want separate checks for
# short as well as long-term permanent cookies
# for first party, third parties, and tracking third parties
CHECKS['general']['cookies'] = {
    'keys': {'cookies_count',},
    'rating': lambda **keys: {
        'description': _('The site is not using cookies.'),
        'classification': Rating('good')
    } if keys['cookies_count'] == 0 else {
        'description': ungettext_lazy(
            'The site is using one cookie.',
            'The site is using %(count)d cookies.', keys['cookies_count']) % {
                'count': keys['cookies_count']},
        'classification':  Rating('bad')},
    'missing': None,
}
# Checks for presence of flash cookies
# 0 cookies: good
# else: bad
# TODO: can we differentiate between first and third parties here as well?
# if not => don't care for now
CHECKS['general']['flashcookies'] = {
    'keys': {'flashcookies_count',},
    'rating': lambda **keys: {
        'description': _('The site is not using flash cookies.'),
        'classification': Rating('good')
    } if keys['flashcookies_count'] == 0 else {
        'description': ungettext_lazy(
            'The site is using one flash cookie.',
            'The site is using %(count)d flash cookies.',
            keys['flashcookies_count']) % {
                'count': keys['flashcookies_count']},
        'classification':  Rating('bad')},
    'missing': None,
}
# Check for embedded third parties
# 0 parties: good
# else: bad
# TODO: is this still the correct key or has this been obsoleted by
# Max's new processing technique?
CHECKS['general']['third_parties'] = {
    'keys': {'third_parties_count',},
    'rating': lambda **keys: {
        'description': _('The site does not use any third parties.'),
        'classification': Rating('good')
    } if keys['third_parties_count'] == 0 else {
        'description': ungettext_lazy(
            'The site is using one third party.',
            'The site is using %(count)d third parties.',
            keys['third_parties_count']) % {
                'count': keys['third_parties_count']},
        'classification':  Rating('bad')},
    'missing': None,
}
# Checks for presence of Google Analytics code
# No GA: good
# else: bad
CHECKS['general']['google_analytics_present'] = {
    'keys': {'google_analytics_present',},
    'rating': lambda **keys: {
        'description': _('The site uses Google Analytics.'),
        'classification': Rating('bad'),
    } if keys['google_analytics_present'] else {
        'description': _('The site does not use Google Analytics.'),
        'classification': Rating('good'),
    },
    'missing': None,
}
# Check for AnonymizeIP setting on Google Analytics
# No GA: neutral
# AnonIP: good
# !AnonIP: bad
CHECKS['general']['google_analytics_anonymizeIP_not_set'] = {
    'keys': {'google_analytics_anonymizeIP_not_set',},
    'rating': lambda **keys: {
        'description': _('The site does not use Google Analytics.'),
        'classification': Rating('neutral')
    } if not keys["google_analytics_present"] else {
        'description': _('The site uses Google Analytics, but does not instruct Google to store anonymized IPs.'),
        'classification': Rating('bad'),
    } if keys['google_analytics_anonymizeIP_not_set'] else {
        'description': _('The site uses Google Analytics, however it instructs Google to store only anonymized IPs.'),
        'classification': Rating('good'),
    },
    'missing': None,
}
# Check for exposed internal system information
# No leaks: good
# Else: bad
CHECKS['general']['leaks'] = {
    'keys': {'leaks',},
    'rating': lambda **keys: {
        'description': _('The site does not disclose internal system information at usual paths.'),
        'classification': Rating('good')
    } if keys['leaks'] == 0 else {
        'description': _('The site discloses internal system information that should not be available.'),
        'classification':  Rating('bad')},
    'missing': None,
}

# Check for the GeoIP of webservers
# Purely informational, no rating associated
CHECKS['privacy']['webserver_locations'] = {
    'keys': {'a_locations',},
    'rating': lambda **keys: describe_locations(
        _('web servers'), keys['a_locations']),
    'missing': None,
}
# Check for the GeoIP of mail servers, if any
# Purely informational, no rating associated
CHECKS['privacy']['mailserver_locations'] = {
    'keys': {'mx_locations',},
    'rating': lambda **keys: describe_locations(
        _('mail servers'), keys['mx_locations']),
    'missing': None,
}
# Check if web and mail servers are in the same country
# Servers in different countries: bad
# Else: None
# TODO Do we want to put an explicit neutral result here?
CHECKS['privacy']['server_locations'] = {
    'keys': {'a_locations', 'mx_locations'},
    'rating': lambda **keys: {
        'description': _('The geo-location(s) of the web server(s) and the mail server(s) are not identical.'),
        'classification': Rating('bad'),
    } if (keys['a_locations'] and keys['mx_locations'] and
          set(keys['a_locations']) != set(keys['mx_locations'])) else {
        'description': _('The geo-location(s) of the web server(s) and the mail server(s) are identical.'),
        'classification': Rating('critical'),
    },
    'missing': None,
}

# Check if final URL is https
# yes: good
# no: critical
CHECKS['ssl']['url_is_https_or_redirects_to_https'] = {
    'keys': {'final_url',},
    'rating': lambda **keys: {
        'description': _('The site url is https or redirects to https.'),
        'classification': Rating('good'),
    } if keys['final_url'].startswith('https') else {
        'description': _('The web server does not redirect to https.'),
        'classification': Rating('critical'),
    },
    'missing': None,
}
# Check if website explicitly redirected us to HTTPS version
# yes: good
# no: bad
# TODO What if https-url was entered by user?
# DH: This does not matter. A HTTPS server that redirects to HTTP is always unacceptable.
CHECKS['ssl']['redirects_from_https_to_http'] = {
    'keys': {'final_https_url'},
    'rating': lambda **keys: {
        'description': _('The web server redirects to HTTP if content is requested via HTTPS.'),
        'classification': Rating('bad'),
    } if (keys['final_https_url'].startswith('http:')) else {
        'description': _('The web server does not redirect to HTTP if content is requested via HTTPS'),
        'classification': Rating('good'),
    },
    'missing': None,
}
# Check if website does not redirect to HTTPS, but offers HTTPS on demand and serves the same content
# HTTPS available and serving same content: good
# HTTPS available but different content: bad
# TODO What is the result if the website forwarded to HTTPS?
# DH: This is one of the tests where I hate that we uselambda functions for this.
CHECKS['ssl']['no_https_by_default_but_same_content_via_https'] = {
    'keys': {'final_url','final_https_url','same_content_via_https'},
    'rating': lambda **keys: {
        'description': _('The site does not use HTTPS by default but it makes available the same content via HTTPS upon request.'),
        'classification': Rating('good'),
    } if (not keys['final_url'].startswith('https') and 
          keys['final_https_url'].startswith('https') and
          keys['same_content_via_https']) else {
        'description': _('The web server does not support HTTPS by default. It hosts an HTTPS site, but it does not serve the same content over HTTPS that is offered via HTTP.'),
        'classification': Rating('bad'),
    } if (not keys['final_url'].startswith('https') and
          keys['final_https_url'].startswith('https') and
          not keys['same_content_via_https']) else None,
    'missing': None,
}
# Check for Perfect Forward Secrecy on Webserver
# PFS available: good
# Else: bad
CHECKS['ssl']['web_pfs'] = {
    'keys': {'web_pfs',},
    'rating': lambda **keys: {
        'description': _('The web server is supporting perfect forward secrecy.'),
        'classification': Rating('good'),
    } if keys['web_pfs'] else {
        'description': _('The web server is not supporting perfect forward secrecy.'),
        'classification': Rating('bad'),
    },
    'missing': None,
}
# Checks for HSTS Preload header
# HSTS present: good
# No HSTS: bad
# TODO CRITICAL Inconsistent and incomplete
CHECKS['ssl']['web_has_hsts_preload_header'] = {
    'keys': {'web_has_hsts_preload_header',},
    'rating': lambda **keys: {
        'description': _('The server uses HSTS to prevent insecure requests.'),
        'classification': Rating('good'),
    } if keys['web_has_hsts_header'] else {
        'description': _('The site is not using HSTS to prevent insecure requests.'),
        'classification': Rating('bad'),
    },
    'missing': None,
}
# Check for HTTP Public Key Pinning Header
# HPKP present: Good, but does not influence ranking (TODO why not?)
# else: bad, but does not influence ranking
# DH: HPKP is not considered mandatory by most other scanners (e.h. qualys)
# cf. our wiki, where it is said that it does not influence the ranking
CHECKS['ssl']['web_has_hpkp_header'] = {
    'keys': {'web_has_hpkp_header',},
    'rating': lambda **keys: {
        'description': _('The site uses Public Key Pinning to prevent attackers from using invalid certificates.'),
        'classification': Rating('good', influences_ranking=False),
    } if keys['web_has_hpkp_header'] else {
        'description': _('The site is not using Public Key Pinning to prevent attackers from using invalid certificates.'),
        'classification': Rating('bad', influences_ranking=False),
    },
    'missing': None,
}
# Check for insecure protocols
# No insecure protocols: Good
# Else: bad
# TODO: split this check into two checks (see wiki!)
CHECKS['ssl']['web_insecure_protocols'] = {
    'keys': {'web_has_protocol_sslv2','web_has_protocol_sslv3'},
    'rating': lambda **keys: {
        'description': _('The server does not support insecure protocols.'),
        'classification': Rating('good'),
    } if not any(keys.values()) else {
        'description': _('The server supports insecure protocols.'),
        'classification': Rating('bad'),
    },
    'missing': None,
}
# Check for secure protocols
# Secure protocols supported: good
# Else: critical
# TODO WTF is this check doing?
# DH: I think we must split this into separate checks, i.e. check each protocol separately
# see wiki
CHECKS['ssl']['web_secure_protocols'] = {
    'keys': {'web_has_protocol_tls1','web_has_protocol_tls1_1','web_has_protocol_tls1_2'},
    'rating': lambda **keys: {
        'description': _('The server supports secure protocols.'),
        'classification': Rating('good'),
    } if any(keys.values()) else {
        'description': _('The server does not support secure protocols.'),
        'classification': Rating('critical'),
    },
    'missing': {
        'description': _('The server does not support secure connections.'),
        'classification': Rating('critical'),
    },
}
# Check for mixed content
# No mixed content: Good
# Else: bad
# TODO I do not like that the else None; it should state that the site does not offer HTTPS therefore Mixed Content checks do not apply (neutral)
CHECKS['ssl']['mixed_content'] = {
    'keys': {'final_url','mixed_content'},
    'rating': lambda **keys: {
        'description': _('The site uses HTTPS, but some objects are retrieved via HTTP (mixed content).'),
        'classification': Rating('bad'),
    } if (keys['mixed_content'] and keys['final_url'].startswith('https')) else {
        'description': _('The site uses HTTPS and all objects are retrieved via HTTPS (no mixed content).'),
        'classification': Rating('good'),
    } if (not keys['mixed_content'] and keys['final_url'].startswith('https')) else None,
    'missing': None,
}
