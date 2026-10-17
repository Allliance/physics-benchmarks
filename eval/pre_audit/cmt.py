"""CMT's original judge contract over the shared evaluation transports."""

import json
from pathlib import Path

from eval import backends


PROMPTS = Path(__file__).parent / "prompts"
CONTRACT_FILES = ("cmt_judge.txt", "cmt_judge_system.txt", "cmt_judge_schema.json")


def make_judge(args):
    prompt = (PROMPTS / CONTRACT_FILES[0]).read_text()
    system = (PROMPTS / CONTRACT_FILES[1]).read_text()
    schema = json.loads((PROMPTS / CONTRACT_FILES[2]).read_text())
    judge = backends.make_judge(args, judge_prompt=prompt, system_prompt=system, schema=schema)

    def evaluate(question, prediction, answer):
        result = judge({**question, "reference_answer": answer}, prediction)
        content = result["judgment"]
        return {"correct_answer": answer, "model_answer": content["extracted_final_answer"],
                "reasoning": content["reasoning"], "correct": content["correct"],
                "confidence": content["confidence"], "actual_model": result["actual_model"]}

    return evaluate
