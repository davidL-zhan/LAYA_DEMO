import importlib
import importlib.util
import unittest


def service_function(test_case, name):
    if importlib.util.find_spec("matching") is None:
        test_case.fail("matching service module has not been implemented")
    matching = importlib.import_module("matching")
    function = getattr(matching, name, None)
    if function is None:
        test_case.fail(f"matching service does not define {name}")
    return function


class FakeRouter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def predict(self, state, questions):
        self.calls.append((state, questions))
        return self.result


class NormalizeInputsTests(unittest.TestCase):
    def test_trims_question_and_preserves_non_empty_knowledge_point_order(self):
        question, knowledge_points = service_function(self, "normalize_inputs")(
            "  求函数最小值  ", [" 二次函数 ", "", " 配方法 ", "二次函数"]
        )

        self.assertEqual(question, "求函数最小值")
        self.assertEqual(knowledge_points, ["二次函数", "配方法", "二次函数"])

    def test_rejects_blank_question(self):
        with self.assertRaisesRegex(ValueError, "题目"):
            service_function(self, "normalize_inputs")(" \t", ["二次函数"])

    def test_rejects_empty_knowledge_points(self):
        with self.assertRaisesRegex(ValueError, "知识点"):
            service_function(self, "normalize_inputs")("求函数最小值", ["", "  "])


class BuildQuestionsTests(unittest.TestCase):
    def test_assigns_stable_keys_and_asks_independent_noul_questions(self):
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
    def test_calls_router_once_and_preserves_raw_response(self):
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
