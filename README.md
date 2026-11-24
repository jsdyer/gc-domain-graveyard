# GC Domain Graveyard

[Open GC Domain Graveyard](https://coolcode.ca/gc-domain-graveyard/)

Recover a Canadian public website from an old name or address and open a dated archival copy.

<!-- coolcode:guide -->
Search for Wheat Board and open a year from the capture timeline. The date belongs to a saved page. The curator’s featured copy and the latest check of the old address have separate labels.
<!-- /coolcode:guide -->

## Sources and coverage

The catalogue begins with six defunct-resource highlights and three dated commission records selected by Library and Archives Canada. “Defunct resources” is the archive's historical category. The app gives the full original URL and the date of the linked copy. Subpaths are important, especially for commission reports.

The Internet Archive CDX query uses the original URL, HTTP 200 captures, one representative per year and an upper date bound of the LAC featured capture. Its replay date and the year in an organization’s title can differ. A failed lookup retains the prior index date. DNS ownership, expiry, parking and content continuity cannot be inferred from a capture or a redirect.

The monthly collector retrieves the LAC highlights, checks the additional historical index, and records one HTTPS response for the original paths on gc.ca or canada.ca. Responses can differ between a browser and the collector. Former independent .ca addresses link only to archival copies. Use the search, response and collection filters together or export the displayed selection.

[Government of Canada Web Archive](https://webarchiveweb.bac-lac.canada.ca/) · [Wayback CDX documentation](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server).

Run `python scripts/refresh.py` to refresh the snapshot, `node --test tests/*.test.mjs` and `python -m unittest discover -s tests` to test, then `python scripts/build.py` to build.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
