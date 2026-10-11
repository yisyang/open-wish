# Modernization planning scenario

This is a supplied assessment, not a runnable game. Treat the observations below
as supplied evidence; do not claim to have inspected missing source or run tests.

The owner wants to rebuild an old persistent business simulation. The legacy PHP
game is a design reference; no player data migration is required. The new backend
only has a health endpoint, the browser repository only has a README, and the
infrastructure repository contains environment notes. No modern gameplay is verified.

OW has 24 current needs covering identity, private learning, companies, facilities,
production, research, B2B, consumer sales, finance, employment, securities, governance,
goals, reports, community, continuity, assistance, catalog, operator support, economic
integrity, offline progression, recovery, reproducible development, and client access.
Their distinct outcomes are confirmed; this exercise is not permission to retire them.

The owner has selected a browser-first rebuild, an isolated private starter economy,
and a shared economy with eight cities. Shared-city play needs timed warehouse freight
over road/rail/air/sea networks. Authoritative money/inventory must remain exact and
retry-safe. Production continues offline with a seven-day queue limit. The main UI
is a touch/keyboard-capable isometric map. Mobile and desktop packages follow later.
A single-instance LAN deployment is available; production hosting follows later.
Numeric rules, art/renderer feasibility, and freight/payment terms need investigation.

The current draft C-001 is titled "Deliver the core pilot", references 18 needs,
and contains these tasks:

1. Select the architecture and economic examples.
2. Establish supported tooling and test identities.
3. Implement exact primitives, versioned catalog, all cities and transactional storage.
4. Implement companies, property, construction, production/cancellation and workers.
5. Implement warehouse freight, routing, fees, capacity and retry-safe arrival.
6. Implement B2B settlement, consumer demand, offline sales and economic reports.
7. Implement the usable isometric browser game and interrupted-command recovery.
8. Containerize and deploy through the LAN GitOps environment.
9. Verify integrated gameplay, concurrency, restore, rollback and operating guidance.

The draft roadmap calls all nine tasks "slice 1". It defers research, employment,
securities, community and native distribution to subsequent changes. All draft tasks
are open. No implementation, passing checks, or result acceptance is supplied.
