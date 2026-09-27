"""考试题与本次候选知识点之间的输入整理、问题构造和 Laya 调用。

模块不保存用户输入，也不负责应用网页上的匹配阈值；它将 Laya 原始结构化结果
原样返回，由调用方用知识点元数据建立可读映射。
"""

from typing import Any


def normalize_inputs(
    question: str, knowledge_points: list[str]
) -> tuple[str, list[str]]:
    """清理本次输入并拒绝缺少题目或有效知识点的请求。

    空白知识点会被忽略；非空项的顺序和重复项会保留，以便结果仍对应用户
    原来的候选列表顺序。
    """
    # 题干整体作为同一个问题状态传给 Router，只清理首尾空白。
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("请输入考试题目内容。")

    # 过滤空行但不去重：同一知识点重复输入时，仍分别得到独立结果。
    clean_points = [point.strip() for point in knowledge_points if point.strip()]
    if not clean_points:
        raise ValueError("请至少输入一个有效知识点。")

    return clean_question, clean_points


def build_questions(
    knowledge_points: list[str],
) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    """为每个候选知识点构造独立的二元判断，并生成回显映射表。

    ``noul`` 是 Laya 的 yes/no 概率问题类型；``kp_N`` 只是在本次请求中的
    稳定键，用于把答案关联回原知识点，并不是跨请求持久化的知识点 ID。
    """
    questions: dict[str, dict[str, str]] = {}
    metadata: list[dict[str, str]] = []

    for index, point in enumerate(knowledge_points, start=1):
        key = f"kp_{index}"
        # 判断标准是“解题是否依赖该知识点”，而不仅是题干是否提到术语。
        questions[key] = {
            "type": "noul",
            "instructions": (
                "判断解答这道考试题时是否需要运用以下知识点："
                f"‘{point}’。如果题目只是提到相关术语，但解答并不依赖它，请判定为否。"
            ),
        }
        # Laya 返回值使用 key；前端通过该表显示用户输入的知识点文本。
        metadata.append({"key": key, "text": point})

    return questions, metadata


def predict_matches(
    router: Any, question: str, knowledge_points: list[str]
) -> dict[str, Any]:
    """一次 Router 调用完成多个知识点判断，并保留 Laya 返回结构。

    每个知识点是一个独立子问题，因此可以同时出现多个匹配项；匹配阈值不在
    此处应用，原始概率由网页根据用户调整的阈值标记为“匹配/不匹配”。
    """
    # 此处再次校验输入，让该函数被 API 之外直接调用时也保持相同边界。
    clean_question, clean_points = normalize_inputs(question, knowledge_points)
    questions, metadata = build_questions(clean_points)

    # 共享题干放在 state，逐知识点判断放在 questions 中并批量提交。
    raw_result = router.predict({"question": clean_question}, questions)

    # 不重组或压缩 Laya 输出，方便 API 调用方检查完整结构化 JSON。
    return {"raw_result": raw_result, "knowledge_points": metadata}
