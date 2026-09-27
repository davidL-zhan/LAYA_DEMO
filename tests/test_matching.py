"""验证输入清理、Laya 子问题构造和批量预测的可观察行为。"""

import importlib
import importlib.util
import unittest


def service_function(test_case, name):
    """延迟导入被测函数，并在函数缺失时给出直观的测试失败信息。"""
    if importlib.util.find_spec("matching") is None:
        test_case.fail("matching service module has not been implemented")
    matching = importlib.import_module("matching")
    function = getattr(matching, name, None)
    if function is None:
        test_case.fail(f"matching service does not define {name}")
    return function


class FakeRouter:
    """用可记录调用参数的替身隔离真实模型加载和网络依赖。"""

    def __init__(self, result):
        self.result = result
        self.calls = []

    def predict(self, state, questions):
        """记录 Router 输入并返回预设结果，模拟一次确定性的推理。"""
        self.calls.append((state, questions))
        return self.result


class NormalizeInputsTests(unittest.TestCase):
    """覆盖空白清理、顺序保留以及无效输入的拒绝规则。"""

    def test_trims_question_and_preserves_non_empty_knowledge_point_order(self):
        """去除首尾空白与空项，但保留顺序和重复知识点。"""
        question, knowledge_points = service_function(self, "normalize_inputs")(
            "  求函数最小值  ", [" 二次函数 ", "", " 配方法 ", "二次函数"]
        )

        self.assertEqual(question, "求函数最小值")
        self.assertEqual(knowledge_points, ["二次函数", "配方法", "二次函数"])

    def test_rejects_blank_question(self):
        """只有空白字符的题目不能作为模型状态。"""
        with self.assertRaisesRegex(ValueError, "题目"):
            service_function(self, "normalize_inputs")(" \t", ["二次函数"])

    def test_rejects_empty_knowledge_points(self):
        """候选项全部为空时应在推理前报出输入错误。"""
        with self.assertRaisesRegex(ValueError, "知识点"):
            service_function(self, "normalize_inputs")("求函数最小值", ["", "  "])


class BuildQuestionsTests(unittest.TestCase):
    """检查每个候选知识点是否映射到独立且可回溯的二元问题。"""

    def test_assigns_stable_keys_and_asks_independent_noul_questions(self):
        """键按输入顺序编号，问题类型和判断说明符合业务语义。"""
        questions, metadata = service_function(self, "build_questions")(
            ["二次函数", "配方法"]
        )

        self.assertEqual(list(questions), ["kp_1", "kp_2"])
        self.assertEqual([item["text"] for item in metadata], ["二次函数", "配方法"])
        self.assertTrue(all(item["type"] == "noul" for item in questions.values()))
        self.assertIn("二次函数", questions["kp_1"]["instructions"])
        self.assertIn("配方法", questions["kp_2"]["instructions"])
        self.assertIn("解答", questions["kp_1"]["instructions"])


class PredictMatchesTests(unittest.TestCase):
    """确保多个子问题通过一次 Router 调用提交且原始结果不被改写。"""

    def test_calls_router_once_and_preserves_raw_response(self):
        """题目被清理后只调用一次，输出保留原始对象并附上知识点映射。"""
        raw_result = {
            "answers": {"kp_1": {"noul": 0.82}},
            "routing": {"model": "multilingual"},
        }
        router = FakeRouter(raw_result)

        response = service_function(self, "predict_matches")(
            router, " 求最小值 ", [" 二次函数 "]
        )

        self.assertEqual(len(router.calls), 1)
        self.assertEqual(router.calls[0][0], {"question": "求最小值"})
        self.assertEqual(list(router.calls[0][1]), ["kp_1"])
        self.assertIs(response["raw_result"], raw_result)
        self.assertEqual(
            response["knowledge_points"], [{"key": "kp_1", "text": "二次函数"}]
        )


if __name__ == "__main__":
    unittest.main()
