```mermaid
flowchart TD
A[Program starts] --> B["Parse args (defaults):
--input-glob = sample_data/ioc_feed_page_*.json
--csv-out = ioc_report.csv
--json-out = ioc_report.json
--max-age-days = 30"]
B --> C{Is glob file list empty?}
C -- Yes --> X[output no matches message and exit]
C -- No --> NOW[Set now = current UTC time in main]
NOW --> D

subgraph Read
D[Load next JSON file; skip and show warning if file cannont be read; count page] --> E[Yield next IOC entry; count raw record]
end

subgraph Filter
E --> F{Severity is critical or high? skip if entry not fomatted properly}
F -- Yes --> G[parse_ts last_seen to UTC-aware datetime]
G --> H{"now - max-age-days <= last_seen <= now?"}
end

subgraph Normalize
H -- Yes --> I["parse_ts then format_ts on first_seen and last_seen
Shape: indicator, type, severity, first_seen, last_seen, source"]
I --> J[Append to filtered/normalized list]
end

F -- No --> L[Drop entry]
H -- No: too old or future-dated --> L

J --> M{More entries in file?}
L --> M
M -- Yes --> E
M -- No --> N{More files?}
N -- Yes --> D

subgraph Dedupe
N -- No --> O[Group filtered/normalized list by indicator]
O --> P["For each indicator keep entry with most recent last_seen
(compare parsed datetimes, not strings)
On a tie keep the entry already present"]
P --> Q[Final deduped list (sort it)]
end

subgraph Report
Q --> S[Write CSV to --csv-out path]
S --> T[Write JSON to --json-out path]
end
T --> V

subgraph Summary
V["Print:
Total raw records across N pages
Total filtered records
Total deduped records
Wrote N deduped records to csv and json"]
end

V --> W[Exit program]

subgraph Helpers["Timestamp helpers (shared by Filter and Normalize)"]
PT["parse_ts accepts:
2026-09-25 00:00:00
2026-10-10T00:00:00
2026-10-07T00:00:00Z
No timezone means UTC"] --> FT["format_ts outputs:
2026-10-07T00:00:00Z"]
end
```
