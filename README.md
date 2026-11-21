[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/erlansyahm90-code/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/erlansyahm90-code/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

Entry for the [make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318): a program that writes one invented passport spread to `/output/entry.png`.

## The document

An open passport spread for the **Republic of Aldruna**, a fictional North Atlantic island nation (capital Skardvik). Left page: the data page of holder Marit Solveig Eldvik — portrait, biographical data, a machine-readable zone with valid ICAO 9303 check digits, a signature, and an endorsement licensing her to crew fishing vessels in Aldruna waters. Right page: the visas page, with arrival/departure stamp pairs from three neighbouring countries — Iceland (Keflavík, June 2023), Norway (Bergen, October 2024) and the United Kingdom (Aberdeen, April 2025) — every stamp dated after the passport's issue (14 March 2023), plus a Skardvik port-tax fee stamp.

## How it works

- `build_passport.py` renders `entry.png` (1024×1024) from scratch with PIL: the portrait, coat of arms, guilloche background, stamps and MRZ are all drawn in code — no downloaded assets.
- `main.py` (stdlib only, offline) copies `entry.png` to `/output/entry.png`.

## Verify

```sh
python3 build_passport.py   # re-render entry.png
python3 main.py             # writes /output/entry.png
```
