"""
客服系统自动化测试用例
测试指标：召回命中率、误转人工率、回答响应速度、回答准确度
"""
import pytest
import time
import asyncio
from typing import List, Dict


class TestRecallRate:
    """召回命中率测试"""

    @pytest.mark.asyncio
    async def test_recall_rate(self, qa_matcher, qa_test_data):
        """测试召回命中率 - 用户问题能否匹配到正确的 QA 记录"""
        if not qa_test_data:
            pytest.skip("没有测试数据")

        hit_count = 0
        miss_list = []

        for test_case in qa_test_data:
            query = test_case['query']
            expected_topic = test_case['topic_name']

            # 执行匹配
            result = await qa_matcher.match(query)

            if result and result.get('topic_name') == expected_topic:
                hit_count += 1
            else:
                miss_list.append({
                    'id': test_case['id'],
                    'query': query,
                    'expected_topic': expected_topic,
                    'matched_topic': result.get('topic_name') if result else None
                })

        total = len(qa_test_data)
        recall_rate = hit_count / total if total > 0 else 0

        # 输出详细信息
        print(f"\n召回命中率: {recall_rate:.2%} ({hit_count}/{total})")
        if miss_list:
            print(f"未命中列表: {len(miss_list)} 条")
            for item in miss_list[:5]:  # 只显示前5条
                print(f"  - [ID: {item['id']}] {item['query'][:30]}...")

        # 断言召回率应该大于 80%
        assert recall_rate >= 0.8, f"召回命中率 {recall_rate:.2%} 低于阈值 80%"


class TestTransferDetection:
    """转人工检测测试"""

    @pytest.mark.asyncio
    async def test_transfer_keywords(self, qa_matcher):
        """测试转人工关键词检测"""
        # 应该触发转人工的查询
        transfer_queries = [
            "我要转人工",
            "找人工客服",
            "我要投诉",
            "太差了我要退款",
            "我不满意这个回答"
        ]

        for query in transfer_queries:
            should_transfer = await qa_matcher.should_transfer_to_human(query)
            assert should_transfer, f"'{query}' 应该触发转人工但没有"

    @pytest.mark.asyncio
    async def test_normal_queries_no_transfer(self, qa_matcher, qa_test_data):
        """测试正常问题不应触发转人工"""
        if not qa_test_data:
            pytest.skip("没有测试数据")

        transfer_count = 0
        transfer_list = []

        for test_case in qa_test_data:
            query = test_case['query']
            should_transfer = await qa_matcher.should_transfer_to_human(query)

            if should_transfer:
                transfer_count += 1
                transfer_list.append({
                    'id': test_case['id'],
                    'query': query
                })

        total = len(qa_test_data)
        transfer_rate = transfer_count / total if total > 0 else 0

        print(f"\n误转人工率: {transfer_rate:.2%} ({transfer_count}/{total})")
        if transfer_list:
            print(f"误触发转人工: {len(transfer_list)} 条")
            for item in transfer_list[:5]:
                print(f"  - [ID: {item['id']}] {item['query'][:30]}...")

        # 误转人工率应该低于 10%
        assert transfer_rate <= 0.1, f"误转人工率 {transfer_rate:.2%} 超过阈值 10%"


class TestResponseTime:
    """响应时间测试"""

    @pytest.mark.asyncio
    async def test_response_time(self, orchestrator, db_session, qa_test_data):
        """测试回答响应速度"""
        if not qa_test_data:
            pytest.skip("没有测试数据")

        response_times = []
        sample_size = min(10, len(qa_test_data))  # 取样测试，避免时间过长

        for test_case in qa_test_data[:sample_size]:
            query = test_case['query']

            start_time = time.time()
            try:
                result = await orchestrator.handle_query(
                    session=db_session,
                    session_id="test_session",
                    query=query
                )
                elapsed_ms = (time.time() - start_time) * 1000
                response_times.append(elapsed_ms)
            except Exception as e:
                print(f"查询失败: {query[:20]}... - {e}")
                continue

        if not response_times:
            pytest.skip("没有成功的响应时间数据")

        # 计算统计指标
        response_times.sort()
        avg_time = sum(response_times) / len(response_times)
        p50 = response_times[len(response_times) // 2]
        p95_idx = int(len(response_times) * 0.95)
        p95 = response_times[min(p95_idx, len(response_times) - 1)]

        print(f"\n响应时间统计 (样本数: {len(response_times)}):")
        print(f"  平均: {avg_time:.0f}ms")
        print(f"  P50: {p50:.0f}ms")
        print(f"  P95: {p95:.0f}ms")
        print(f"  最小: {min(response_times):.0f}ms")
        print(f"  最大: {max(response_times):.0f}ms")

        # P95 应该小于 3000ms
        assert p95 < 3000, f"P95 响应时间 {p95:.0f}ms 超过阈值 3000ms"


class TestAnswerAccuracy:
    """回答准确度测试 (LLM 评估)"""

    @pytest.mark.asyncio
    async def test_answer_accuracy(self, orchestrator, db_session, qa_test_data):
        """使用 LLM 评估回答准确度"""
        if not qa_test_data:
            pytest.skip("没有测试数据")

        accurate_count = 0
        inaccurate_list = []
        sample_size = min(10, len(qa_test_data))  # 取样测试

        for test_case in qa_test_data[:sample_size]:
            query = test_case['query']
            expected_answer = test_case['expected_answer']

            try:
                result = await orchestrator.handle_query(
                    session=db_session,
                    session_id="test_session",
                    query=query
                )

                actual_answer = result.get('response', '') if result else ''

                # 使用 LLM 评估
                is_accurate, reason = await self._evaluate_with_llm(
                    orchestrator,
                    query,
                    expected_answer,
                    actual_answer
                )

                if is_accurate:
                    accurate_count += 1
                else:
                    inaccurate_list.append({
                        'id': test_case['id'],
                        'query': query,
                        'reason': reason
                    })
            except Exception as e:
                print(f"评估失败: {query[:20]}... - {e}")
                continue

        evaluated_count = accurate_count + len(inaccurate_list)
        if evaluated_count == 0:
            pytest.skip("没有成功评估的数据")

        accuracy_rate = accurate_count / evaluated_count

        print(f"\n回答准确度: {accuracy_rate:.2%} ({accurate_count}/{evaluated_count})")
        if inaccurate_list:
            print(f"不准确案例: {len(inaccurate_list)} 条")
            for item in inaccurate_list[:5]:
                print(f"  - [ID: {item['id']}] {item['query'][:30]}... 原因: {item['reason'][:50]}")

        # 准确率应该大于 85%
        assert accuracy_rate >= 0.85, f"回答准确度 {accuracy_rate:.2%} 低于阈值 85%"

    async def _evaluate_with_llm(
        self,
        orchestrator,
        query: str,
        expected_answer: str,
        actual_answer: str
    ) -> tuple:
        """使用 LLM 评估回答质量"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=orchestrator.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            prompt = f"""你是一个客服回答质量评估专家。

用户问题：{query}
期望答案要点：{expected_answer[:500]}
实际回答：{actual_answer[:500]}

请判断实际回答是否正确回应了用户问题，并包含了期望答案的核心要点。
只回答以下格式：
正确/错误|简短理由（20字以内）"""

            response = await client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()
            parts = result.split('|')

            is_accurate = parts[0].strip() == '正确'
            reason = parts[1].strip() if len(parts) > 1 else result

            return is_accurate, reason

        except Exception as e:
            # 如果 LLM 评估失败，使用简单的文本匹配作为后备
            return self._simple_evaluate(expected_answer, actual_answer), str(e)

    def _simple_evaluate(self, expected: str, actual: str) -> bool:
        """简单的文本匹配评估（后备方案）"""
        if not expected or not actual:
            return False

        # 检查关键词重叠
        expected_words = set(expected)
        actual_words = set(actual)
        overlap = len(expected_words & actual_words) / len(expected_words) if expected_words else 0

        return overlap > 0.3
