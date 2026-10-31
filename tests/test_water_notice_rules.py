import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path


CONTRACT_PATH = Path(__file__).parents[1] / "contracts" / "water_notice.py"


class FakeReturn:
    def __init__(self, calldata):
        self.calldata = calldata


class FakeUserError(Exception):
    pass


class FakePublic:
    @staticmethod
    def write(function):
        return function

    @staticmethod
    def view(function):
        return function


class FakeRuntime:
    def __init__(self, pages):
        self.pages = pages

    def render(self, url, mode="html"):
        if url not in self.pages:
            raise OSError("mock page not found")
        return self.pages[url]

    @staticmethod
    def exec_prompt(prompt, response_format=None):
        target = prompt.split(
            "Target area to check:\n", 1
        )[1].split("\n\nPage content:", 1)[0].strip()

        page = prompt.split(
            "\nPage content:\n", 1
        )[1].split("\n\nReturn only JSON with exactly these keys:", 1)[0]

        lowered = page.lower()

        if "lifted" in lowered or "rescinded" in lowered or "ended" in lowered:
            kind = "LIFTED"
        elif "boil water advisory" in lowered or "boil your tap water" in lowered:
            kind = "ACTIVE"
        else:
            kind = "OTHER"

        target_lower = target.lower()
        target_number = next(
            (token for token in target_lower.split() if token.isdigit()),
            "",
        )
        target_street = (
            target_lower.replace(target_number, "").strip()
            if target_number
            else target_lower
        )

        street_match = target_street in lowered
        number_match = not target_number or target_number in lowered
        match = "MATCH" if street_match and number_match else "NO_MATCH"

        quote = "Boil Water Advisory"
        if quote.lower() not in lowered:
            quote = page[: min(80, len(page))]

        return json.dumps(
            {
                "notice_kind": kind,
                "area_match": match,
                "evidence_quote": quote,
            }
        )


class FakeVM:
    Return = FakeReturn
    UserError = FakeUserError

    def __init__(self, runtime):
        self.runtime = runtime

    def run_nondet_unsafe(self, leader_fn, validator_fn):
        result = leader_fn()
        if not validator_fn(FakeReturn(result)):
            raise AssertionError("mock validator rejected leader output")
        return result


class ContractTests(unittest.TestCase):
    def load_contract(self, pages):
        gl = types.SimpleNamespace(
            Contract=object,
            u256=int,
            public=FakePublic(),
            nondet=types.SimpleNamespace(
                web=FakeRuntime(pages),
                exec_prompt=FakeRuntime.exec_prompt,
            ),
        )
        gl.vm = FakeVM(gl.nondet)

        fake_module = types.ModuleType("genlayer")
        fake_module.gl = gl
        fake_module.u256 = int
        fake_module.__all__ = ["gl", "u256"]

        original = sys.modules.get("genlayer")
        sys.modules["genlayer"] = fake_module

        try:
            spec = importlib.util.spec_from_file_location(
                "water_notice_under_test",
                CONTRACT_PATH,
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.WaterNotice(), gl
        finally:
            if original is None:
                sys.modules.pop("genlayer", None)
            else:
                sys.modules["genlayer"] = original

    def test_active_notice_for_matching_area(self):
        url = "https://www.portagemi.gov/notice/active"
        page = "Boil Water Advisory for 5423, 5427, and 5429 Meredith Street"
        contract, _ = self.load_contract({url: page})

        result = json.loads(
            contract.assess_notice(url, "5427 Meredith Street")
        )

        self.assertEqual(result["decision"], "ACTIVE_NOTICE_FOR_AREA")
        self.assertEqual(result["sequence"], 1)

    def test_lifted_notice_for_matching_area(self):
        url = "https://portagemi.gov/notice/lifted"
        page = (
            "Boil Water Advisory - Lifted for "
            "5423, 5427, and 5429 Meredith Street"
        )
        contract, _ = self.load_contract({url: page})

        result = json.loads(
            contract.assess_notice(url, "5427 Meredith Street")
        )

        self.assertEqual(result["decision"], "LIFTED_NOTICE_FOR_AREA")

    def test_different_area_does_not_match(self):
        url = "https://www.portagemi.gov/notice/active"
        page = "Boil Water Advisory for Meredith Street"
        contract, _ = self.load_contract({url: page})

        result = json.loads(
            contract.assess_notice(url, "Tiffin Street")
        )

        self.assertEqual(result["decision"], "NOTICE_NAMES_OTHER_AREA")

    def test_rejects_non_portage_host(self):
        contract, gl = self.load_contract({})

        with self.assertRaises(gl.vm.UserError):
            contract.assess_notice(
                "https://example.com/notice",
                "Meredith Street",
            )

    def test_rejects_invalid_area_length(self):
        contract, gl = self.load_contract({})

        with self.assertRaises(gl.vm.UserError):
            contract.assess_notice(
                "https://www.portagemi.gov/notice",
                "x",
            )


if __name__ == "__main__":
    unittest.main()
