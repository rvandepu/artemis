# Changelog

## [UNRELEASED] - YYYY-MM-DD
### Added
- Bug report and feature request issue templates
- Code of conduct

### Changed
- Done misc updates on README
- Moved static js libraries to CDN

### Fixed
- Misc code quality improvements
- Fetch API support for older browsers

### Removed
- ACKS file (moved to README in-line)

### Deprecated
- Removed deprecated graphql query

### Security
- Bumped flask from 0.12.2 to 1.0.2 in /frontend
- Bumped requests from 2.19.1 to 2.21.0 in /frontend

## [1.0] - 2018-12-20
### Added (initial Apollo release)
* Monitor micro-service, providing real-time monitoring of the changes in the BGP routes of the network's prefixes.
Support for the following route collectors and interfaces:
  * [RIPE RIS](http://stream-dev.ris.ripe.net/demo2) (real-time streaming)
  * [BGPStream](https://bgpstream.caida.org/), supporting:
    * RouteViews and RIPE RIS (30-minute delayed streaming)
    * BetaBMP (real-time streaming)
    * Historical updates replayed from csv files (historical streaming)
  * [exaBGP](https://github.com/Exa-Networks/exabgp) (real-time streaming)
* Configuration micro-service, dealing with reading the ARTEMIS configuration from a file (YAML); the file
contains information about: prefixes, ASNs, monitors and ARTEMIS rules (e.g., "ASX advertises prefix P to ASY").
* Detection micro-service, providing real-time detection of BGP prefix hijacking attacks/events of the following types:
  * exact-prefix type-0/1
  * sub-prefix (of any type)
  * squatting attacks
* Mitigation micro-service, providing manual or manually controlled mitigation of BGP prefix hijacking attacks.
* Observer micro-service, dealing with the monitoring of the changes in the ARTEMIS configuration file, triggering the reloading of the affected micro-services.
* Scheduler micro-service, providing a clock service for periodical messages consumed by different micro-services.
* Postgres DB access micro-service, providing programmatic R+W access to the main database of ARTEMIS.
* Supervisord for managing the backend services of the system as processes, and listener micro-service to listen for changes in the process status (e.g., running --> stopped).
* Integration of Monitor, Configuration, Detection, Mitigation, Observer, Scheduler and Postgres DB micro-service in ARTEMIS
"backend".
* Integrated HTTPS frontend/web interface used by the network administrator to:
  * register to the system (ADMIN role: R+W access, VIEWER role: R access)
  * provide configuration information (ASNs, prefixes, routing policies, etc.) via a web-based text editor
  * comment on the configuration file that is used as the system input
  * view and compare past configuration files, using their timestamps to disambiguate them
  * control Monitor, Detection and Mitigation micro-services (start/stop)
  * view the status of all micro-services live (on/off/uptime)
  * view in real-time the BGP updates (announcements/withdrawals) related to the (configured) IP prefixes of interest,
with the following capabilities:
    * per-prefix grouping
    * live update/offline mode
    * time window tuning
    * number of visible entries tuning
    * paginated viewing
    * basic information per update (timestamp, prefix, origin AS, AS-path, peer AS, route collector service, type, hijack, status)
    * auxiliary information per route collector that has seen the BGP update(s) (mouse hover)
    * auxiliary information per update (original AS-path, communities, hijack key, matched prefix)
    * ASN, name, private or not, and countries of operation for origin and peer ASes, as well as ASes present on an AS-path (mouse hover)
    * sorting per update timestamp
    * searching updates using the prefix, origin AS, peer AS, service, and/or update type fields
    * downloading the (filtered) bgp updates table in json format
    * displaying the distinct values involved in the prefix, origin AS, peer AS, service and type fields
  * view in real-time the BGP prefix hijacking events related to the (configured) IP prefixes of interest,
with the following capabilities:
    * per-prefix grouping
    * live update/offline mode
    * time window tuning
    * number of visible entries tuning
    * paginated viewing
    * basic information per hijack (time detected, status, prefix, type, hijack AS, number of peers seen, number of ASes infected, seen)
    * auxiliary information per hijack (matched prefix, first matched configuration, hijack key, time started, time last updated, time ended,
time mitigation started, peer ASes that saw announcements/withdrawals, BGP updates related to this hijack)
    * buttons to mark an individual hijack as seen, resolve, mitigate or ignore it
    * comment box to associate a hijack with a certain comment
    * group actions to mark multiple hijacks as seen/not seen, ignored, or resolved
    * ASN, name, private or not, and countries of operation for hijack ASes (mouse hover)
    * sorting per time detected timestamp
    * searching hijacks using the prefix, hijack type, and/or hijack AS fields
    * downloading the (filtered) hijacks table in json format
    * displaying the distinct values involved in the prefix, type and hijack AS fields
  * view the status of a hijack: ongoing, ignored, resolved, under mitigation, withdrawn, outdated
  * automatic characterization of a hijack as withdrawn if all the monitor peers that saw a hijack update saw also a withdrawal
  * automatic characterization of a hijack as outdated if the configuration that triggered the hijack is outdated
  * view DB statistics (total/unhandled BGP updates, total/resolved/ignored/under mitigation/ongoing/ignored/withdrawn/outdated/seen hijacks)
  * view help boxes for every field used in the system (mouse hover)
  * view additional login information
  * change password
  * manage users
  * view visualization of per-prefix AS-level graphs (until the first hop neighbor), according to configuration
* User interface for both mobile and desktop environments
* Support for both IPv4 and IPv6 prefixes
* Support for handling AS-Sets, Confederations, AS sequences, path prepending, loops, etc. appearing during the monitoring + detection processes
* Support for email/syslog/other notifications for new hijacks
* Daily backups of the ARTEMIS DB
* Scalable RabbitMQ message bus (container) for the message passing and queueing for all involved micro-services and containers
* Timescale + Postgres container for persistent storage and efficient data indexing
* Postgrest container for REST API to Postgres DB
* Hasura graphql container for asynchronous access to Postgres DB
* Pg_amqp bridge container for asynchronous communication between Postgres DB and RabbitMQ
* Redis DB for ephemeral storage in the backend
* NGINX server for terminating SSL connections before propagating to the frontend
* Gunicorn for HTTP request load balancing
* Flask for the frontend (used as proxy)
* Support for automated migration of the ARTEMIS DB to new versions
* Cython support for optimized performance
* JWT authentication in graphql
* DB access optimized via indexes
* Composition of multiple containers via docker-compose
* Support for running multiple detector instances
* Optional support for Kubernetes setups (single physical machine)

### Changed
- NA (Not Applicable)

### Fixed
- NA

### Removed
- NA

### Deprecated
- NA

### Security
- NA

# TEMPLATE FOR NEW RELEASES
## [RELEASE_VERSION] - YYYY-MM-DD
### Added
- TBD (Added a new feature)

### Changed
- TBD (Changed existing functionality)

### Fixed
- TBD (bug-fix)

### Removed
- TBD (removed a feature)

### Deprecated
- TBD (soon-to-be removed feature)

### Security
- TBD (addressing vulnerability)

## ACKS
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
