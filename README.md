# WaterNotice

WaterNotice is a standalone GenLayer Intelligent Contract prototype that interprets one official municipal drinking-water notice for a specified street or address.

For the submitted notice page, it records whether the page explicitly describes an active boil-water advisory, says that an advisory was lifted, names another area, or does not provide enough evidence.

## Why GenLayer

Notice pages use natural language, and an address may need to be matched against a named street or an explicit address range. The leader and validators independently read the selected page and classify the notice and target-area relationship.

The validator checks the leader's structured decision against its own classification and verifies that the leader's evidence quote appears in its independently retrieved page. Contract state changes only after the consensus call returns.

## Contract methods

- `assess_notice(source_url, target_area)` assesses one notice page and stores the latest result.
- `get_latest_record()` returns the latest assessment as JSON text.
- `get_assessment_count()` returns the number of assessments recorded.

The contract accepts HTTPS URLs under `portagemi.gov` only. It stores the latest result and a monotonically increasing count, not an unbounded history.

## Decision values

- `ACTIVE_NOTICE_FOR_AREA`
- `LIFTED_NOTICE_FOR_AREA`
- `NOTICE_NAMES_OTHER_AREA`
- `NOT_A_WATER_ADVISORY`
- `UNRESOLVED`

## Important limitation

`ACTIVE_NOTICE_FOR_AREA` means the submitted page was interpreted as describing an active notice for the target area. It does not prove the notice is still current. `LIFTED_NOTICE_FOR_AREA` means the submitted page explicitly says the advisory was lifted.

`UNRESOLVED` does not mean water is safe or unsafe. This contract does not certify water quality and does not replace official public-health guidance. Its result is limited to the page and area submitted for assessment.

## Example pages for Studio testing

These historical City of Portage pages are useful for testing both notice classifications. They do not describe current water conditions.

- Active-notice page: `https://www.portagemi.gov/m/newsflash/Archive/Item/1500?arcId=2681`
- Lifted-notice page: `https://www.portagemi.gov/m/newsflash/Archive/Item/1511?arcId=2699`
- Target area for both: `5427 Meredith Street`

Expected decisions are `ACTIVE_NOTICE_FOR_AREA` and `LIFTED_NOTICE_FOR_AREA`, respectively, if live retrieval and validator consensus succeed.

## Local checks

Run these commands from the project root:

```bash
python -m unittest discover -s tests -v
python -m py_compile contracts/water_notice.py
```

The tests use a mock GenLayer interface. They are local regression tests, not GenVM or Studio validation. The contract must still be tested with full consensus in Studio before describing it as live-validated.
