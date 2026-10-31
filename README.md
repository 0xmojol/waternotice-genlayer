# WaterNotice

WaterNotice is a GenLayer Intelligent Contract prototype for interpreting one official City of Portage, Michigan water-notice page against a target street or address.

It records an interpretation of the submitted page. It is not a live water-safety oracle and does not certify that water is safe or unsafe.

## Why GenLayer

A public notice may express its status in natural language, and a target address may fall within an explicit street or address range. The contract fetches the submitted official page, asks GenLayer to classify the notice and target-area relationship, validates the structured result and evidence quote, then stores the agreed assessment.

## Contract interface

- `assess_notice(source_url, target_area)` reads one page on the official `portagemi.gov` domain and stores the latest structured assessment.
- `get_latest_record()` returns the latest assessment as JSON text.
- `get_assessment_count()` returns the number of assessment writes.

Possible decisions:

- `ACTIVE_NOTICE_FOR_AREA`
- `LIFTED_NOTICE_FOR_AREA`
- `NOTICE_NAMES_OTHER_AREA`
- `NOT_A_WATER_ADVISORY`
- `UNRESOLVED`

The contract stores only the latest record and a monotonically increasing count. It does not maintain an unbounded history.

## Safety and source limitations

`ACTIVE_NOTICE_FOR_AREA` means that the specific submitted page was interpreted as an active notice for the target area. It does not prove that the notice is still current. `LIFTED_NOTICE_FOR_AREA` means that the submitted page explicitly says the advisory was lifted. `UNRESOLVED` is not a safe/unsafe finding. No result certifies water quality or replaces official public-health guidance.

The source URL is restricted to HTTPS pages under `portagemi.gov`. This checks the hostname only; it does not cryptographically authenticate the author or prove that the page is current. The assessment is only as reliable as the selected source and the content available to GenLayer's web renderer.

## Studio validation

The contract was deployed and upgraded on Studionet at:

- Contract: [`0x110E0Eb800c0C2155cF9BA6E9B5b38e4910c8A75`](https://explorer-studio.genlayer.com/address/0x110E0Eb800c0C2155cF9BA6E9B5b38e4910c8A75)
- Deployment transaction: [`0xdb096cd0df671587e35b89b33f65bafe79bae3e296ef10a95a3de2f35dfad0cc`](https://explorer-studio.genlayer.com/tx/0xdb096cd0df671587e35b89b33f65bafe79bae3e296ef10a95a3de2f35dfad0cc)
- JSON-response handling upgrade: [`0x944a3fc767e2b370183d4f6e66a9e90afe32f9b14029142aa89a3f1dec628df1`](https://explorer-studio.genlayer.com/tx/0x944a3fc767e2b370183d4f6e66a9e90afe32f9b14029142aa89a3f1dec628df1)

Observed Studio checks on October 31, 2026:

- A call using the official general News Flash RSS feed returned `NOT_A_WATER_ADVISORY` with an excerpt about a Portage Road gas-main replacement. This classifies that returned news item only; it does not prove that no water advisory exists elsewhere or certify water safety.
- Calls using two older Meredith Street archive pages returned `UNRESOLVED`. GenLayer's rendered page content included unrelated related-news content or a `Loading` placeholder instead of readable notice text. These calls do not validate the active or lifted outcomes.
- The assessment counter and latest-record view methods returned the persisted state successfully.

The archive URLs below are historical examples, not current water-status sources. Their page bodies may be image-based or dynamically loaded, so Studio may correctly return `UNRESOLVED` when it cannot access clear notice evidence.

## Local checks

Run the mock-interface regression suite from the project root:

```bash
python -m unittest discover -s tests -v
python -m py_compile contracts/water_notice.py
```

The five unit tests exercise the contract method using a fake GenLayer interface. They are useful regression checks, but they are not GenVM or Studio validation and do not prove live active/lifted classification.
