import json
from pathlib import Path
import unittest

from eval.datasets import DATA_ROOT, load_dataset
from eval.pre_audit import load_benchmark


class DataSnapshotTests(unittest.TestCase):
    def test_manifest_files_and_counts(self):
        manifest = json.loads((DATA_ROOT / "manifest.json").read_text())
        expected = {
            "phybench": (100, 87), "hle-physics": (202, 116),
            "prism": (100, 74), "ugphysics": (100, 82),
            "cmt": (50, 49), "critpt": (54, 54),
        }
        for name, (pre_count, post_count) in expected.items():
            with self.subTest(name=name):
                entries = manifest["benchmarks"][name]
                for entry in entries.values():
                    path = DATA_ROOT / entry["file"]
                    self.assertTrue(path.is_file())
                self.assertEqual(len(load_benchmark(name).problems), pre_count)
                self.assertEqual(len(load_dataset(name)[0]), post_count)

    def test_cmt_and_critpt_explicit_post_audit_exclusions(self):
        manifest = json.loads((DATA_ROOT / "manifest.json").read_text())["benchmarks"]
        self.assertEqual(manifest["cmt"]["post_audit"]["excluded"],
                         [{"id": "14", "reason": "UNREPAIRABLE"}])
        self.assertEqual({item["id"] for item in
                          manifest["critpt"]["post_audit"]["excluded"]},
                         {"41", "46"})

    def test_critpt_review_status(self):
        rows, _ = load_dataset("critpt")
        self.assertFalse({"00", "38", "54"} & {row["id"] for row in rows})
        self.assertNotIn("00", {problem.id for problem in load_benchmark("critpt").problems})

        audit_root = DATA_ROOT.parents[1] / "audit"
        verdicts = json.loads((audit_root / "critpt/verdicts.json").read_text())
        self.assertLessEqual({"38", "54"}, set(verdicts["not_reviewed_problems"]))
        reviewed = set().union(*(set(verdicts[key]) for key in
                                ("correct_problems", "repairable_problems",
                                 "unrepairable_problems")))
        self.assertEqual(len(reviewed), 56)
        self.assertEqual(reviewed, set(json.loads(
            (audit_root / "dataset_ids.json").read_text())["critpt"]["all_ids"]))
        self.assertEqual(reviewed - set(verdicts["unrepairable_problems"]), {row["id"] for row in rows})

    def test_critpt_paper_attributions_match_final_adjudications(self):
        audit_root = DATA_ROOT.parents[1] / "audit/critpt"
        verdicts = json.loads((audit_root / "verdicts.json").read_text())
        decisions = json.loads((audit_root / "adjudications.json").read_text())["challenges"]
        self.assertEqual(len(decisions), 56)
        for group, status, count in (
                ("correct_problems", "clean", 35),
                ("repairable_problems", "repairable", 19),
                ("unrepairable_problems", "unrepairable", 2)):
            expected = {qid for qid, decision in decisions.items() if decision["problem"] == status}
            self.assertEqual(set(verdicts[group]), expected)
            self.assertEqual(len(expected), count)
        model_errors = {qid for qid, decision in decisions.items() if decision["model"] == "incorrect"}
        self.assertEqual(model_errors, {"06", "16", "18", "58", "60"})
        self.assertLessEqual(model_errors, set(verdicts["correct_problems"]))
        for decision in decisions.values():
            self.assertTrue(decision["reason"].strip())
            if decision["problem"] != "clean":
                self.assertEqual(decision["model"], "none")

        pre = {row["id"]: row for row in map(json.loads,
               (DATA_ROOT / "pre_audit/critpt.jsonl").read_text().splitlines())}
        post = {row["id"]: row for row in load_dataset("critpt")[0]}
        changed = {qid for qid in post if post[qid]["question"] != pre[qid]["question"]}
        self.assertEqual(len(changed), 32)
        self.assertEqual(len(changed & set(verdicts["repairable_problems"])), 19)
        self.assertEqual(len(changed & set(verdicts["correct_problems"])), 13)

if __name__ == "__main__":
    unittest.main()
