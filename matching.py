"""Business logic for mapping exam questions to temporary knowledge points."""

from typing import Any


def normalize_inputs(
    question: str, knowledge_points: list[str]
) -> tuple[str, list[str]]:
    """Trim the question and knowledge points, rejecting an empty request."""
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("请输入考试题目内容。")

    clean_points = [point.strip() for point in knowledge_points if point.strip()]
    if not clean_points:
        raise ValueError("请至少输入一个有效知识点。")

    return clean_question, clean_points


def build_questions(
    knowledge_points: list[str],
) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    """Build one independent yes/no probability question for each topic."""
    questions: dict[str, dict[str, str]] = {}
    metadata: list[dict[str, str]] = []

    for index, point in enumerate(knowledge_points, start=1):
        key = f"kp_{index}"
        questions[key] = {
            "type": "noul",
            "instructions": (
                "判断解答这道考试题时是否需要运用以下知识点："
                f"‘{point}’。如果题目只是提到相关术语，但解答并不依赖它，请判定为否。"
            ),
        }
        metadata.append({"key": key, "text": point})

    return questions, metadata


def predict_matches(
    router: Any, question: str, knowledge_points: list[str]
) -> dict[str, Any]:
    """Send all knowledge-point decisions in one Router call and preserve its payload."""
    clean_question, clean_points = normalize_inputs(question, knowledge_points)
    questions, metadata = build_questions(clean_points)
    raw_result = router.predict({"question": clean_question}, questions)

    return {"raw_result": raw_result, "knowledge_points": metadata}
