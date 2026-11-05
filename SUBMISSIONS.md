# Submission log

Where this data (and the tool behind it) has been offered to public lists, what came
back, and what is deliberately not being attempted. Statuses below were read from the
GitHub API on 2026-11-05; they are not guesses.

## Submitted on 2026-11-03

| Target | Pull request | State on 2026-11-05 |
|---|---|---|
| `mcuking/Awesome-WebAssembly-Applications` → Inside the browser / Media | [#83](https://github.com/mcuking/Awesome-WebAssembly-Applications/pull/83) | **Merged** 2026-11-03T05:55:06Z. The [README](https://github.com/mcuking/Awesome-WebAssembly-Applications/blob/master/README.md) now carries the ClipFit entry. |
| `mbasso/awesome-wasm` → Demos | [#369](https://github.com/mbasso/awesome-wasm/pull/369) | **Open**, awaiting review. No maintainer comment yet. |
| `brandonhimpfen/awesome-ffmpeg` → GUI Tools | [#38](https://github.com/brandonhimpfen/awesome-ffmpeg/pull/38) | **Closed, not merged.** The maintainer declined it: the empirical validation was "quite limited, with only two measured encoding runs", and the project did "not yet establish sustained maintenance or independent user adoption". They offered to review a future submission with a broader reproducible test set. |

The third response is the reason [`records/site-8mb-10s-reserve.json`](records/site-8mb-10s-reserve.json)
and the "Coverage and limits" section now exist. One extra run does not meet the
maintainer's stated bar, so **no resubmission to that list is being made**. Repeating a
just-declined submission is not a clean link.

## Checked on 2026-11-05, not submitted

- `jacc/awesome-discord` — its `contributing.md` says "If you just created something,
  wait at least 30 days before submitting." The site went live 2026-10-25, which is 11
  days before this check. The rule is not met; the earliest compliant date would be
  2026-11-24. Not submitted.
- `transitive-bullshit/awesome-ffmpeg` — its `contributing.md` 7-day wait is met, but
  the `## JavaScript` section lists libraries and wrappers, not end-user applications,
  and the guide says "Link to the GitHub repo, not npmjs.com". An application entry
  would be off-scope there. Not submitted.
- `torch2424/made-with-webassembly` — the README says "Contributing new projects is
  definitely welcome and super appreciated!" and documents the showcase file format.
  Submitted on 2026-11-05; see the pull request in the table above once created.

## Two things that will sink any of these

- Pasting the same description into every list. Each list has its own house style and
  its own contributing rules; entries are written for the target section, not reused.
- Linking the repo *and* the site in the same line. One link per entry: the site link.
  The repo is what you send when someone asks for the data behind it.
