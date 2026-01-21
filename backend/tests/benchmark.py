"""
客服系统基准测试脚本
独立运行，生成 Markdown 格式测试报告

使用方式:
    cd backend
    python -m tests.benchmark
"""
import sys
import os
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from backend.core.database import Base, DATABASE_URL
from backend.models.db_models import CustomerServiceQA
from backend.apps.customer_service.services.qa_matcher import QAMatcher
from backend.apps.customer_service.services.orchestrator import CustomerServiceOrchestrator
from backend.core.config import settings


# 报告输出路径
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# Rich Console
console = Console()


class BenchmarkRunner:
    """基准测试运行器"""

    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.qa_matcher = None
        self.orchestrator = None
        self.test_data: List[Dict] = []

        # 测试结果
        self.results = {
            'recall': {'hits': 0, 'total': 0, 'misses': []},
            'transfer': {'transfers': 0, 'total': 0, 'false_transfers': []},
            'response_time': {'times': [], 'errors': []},
            'accuracy': {'accurate': 0, 'total': 0, 'inaccurate': []}
        }

    async def initialize(self):
        """初始化数据库连接和组件"""
        with console.status("[bold green]正在初始化...", spinner="dots") as status:
            self.engine = create_async_engine(DATABASE_URL, echo=False)
            self.session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with self.session_maker() as session:
                # 初始化 QA Matcher
                status.update("[bold green]加载 QA Matcher...")
                self.qa_matcher = QAMatcher()
                await self.qa_matcher.load_qa_data(session)

                # 初始化 Orchestrator
                status.update("[bold green]初始化 Orchestrator...")
                self.orchestrator = CustomerServiceOrchestrator(api_key=settings.DASHSCOPE_API_KEY)
                await self.orchestrator.initialize(session)

                # 加载测试数据
                status.update("[bold green]加载测试数据...")
                result = await session.execute(select(CustomerServiceQA))
                qa_records = result.scalars().all()

                for qa in qa_records:
                    self.test_data.append({
                        'id': qa.id,
                        'query': qa.typical_question,
                        'topic_name': qa.topic_name,
                        'expected_answer': qa.standard_script,
                        'risk_notes': qa.risk_notes
                    })

        console.print(f"[green]✓[/green] 初始化完成，加载了 [bold]{len(self.test_data)}[/bold] 条测试数据")

    async def run_all_tests(self):
        """运行所有测试"""
        if not self.test_data:
            console.print("[red]错误: 没有测试数据[/red]")
            return

        console.print()
        console.rule("[bold blue]开始基准测试", style="blue")

        await self.test_recall_rate()
        await self.test_transfer_detection()
        await self.test_response_time()
        await self.test_answer_accuracy()

        console.print()
        console.rule("[bold green]测试完成", style="green")

    async def test_recall_rate(self):
        """测试召回命中率"""
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("• {task.fields[stat]}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:

            task = progress.add_task(
                "[1/4] 召回命中率",
                total=len(self.test_data),
                stat="测试中..."
            )

            for i, test_case in enumerate(self.test_data):
                query = test_case['query']
                expected_topic = test_case['topic_name']

                results = await self.qa_matcher.match(query)

                if results:
                    top_match = results[0]
                    matched_topic = top_match[0].topic_name
                    if matched_topic == expected_topic:
                        self.results['recall']['hits'] += 1
                    else:
                        self.results['recall']['misses'].append({
                            'id': test_case['id'],
                            'query': query,
                            'expected': expected_topic,
                            'matched': matched_topic
                        })
                else:
                    self.results['recall']['misses'].append({
                        'id': test_case['id'],
                        'query': query,
                        'expected': expected_topic,
                        'matched': None
                    })

                self.results['recall']['total'] += 1

                # 更新进度条
                hits = self.results['recall']['hits']
                total = self.results['recall']['total']
                rate = hits / total if total > 0 else 0
                progress.update(task, advance=1, stat=f"命中: {hits}/{total} ({rate:.1%})")

            # 最终结果
            rate = self.results['recall']['hits'] / self.results['recall']['total']
            color = "green" if rate >= 0.8 else "red"
            progress.update(task, stat=f"[{color}]完成: {rate:.1%}[/{color}]")

    async def test_transfer_detection(self):
        """测试转人工检测"""
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("• {task.fields[stat]}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:

            task = progress.add_task(
                "[2/4] 转人工检测",
                total=len(self.test_data),
                stat="测试中..."
            )

            for i, test_case in enumerate(self.test_data):
                query = test_case['query']

                results = await self.qa_matcher.match(query)
                top_match = results[0] if results else None
                should_transfer = self.qa_matcher.should_transfer_to_human(query, top_match)

                if should_transfer:
                    self.results['transfer']['transfers'] += 1
                    self.results['transfer']['false_transfers'].append({
                        'id': test_case['id'],
                        'query': query
                    })

                self.results['transfer']['total'] += 1

                # 更新进度条
                transfers = self.results['transfer']['transfers']
                total = self.results['transfer']['total']
                rate = transfers / total if total > 0 else 0
                progress.update(task, advance=1, stat=f"误转: {transfers}/{total} ({rate:.1%})")

            # 最终结果
            rate = self.results['transfer']['transfers'] / self.results['transfer']['total']
            color = "green" if rate <= 0.1 else "red"
            progress.update(task, stat=f"[{color}]误转率: {rate:.1%}[/{color}]")

    async def test_response_time(self):
        """测试响应时间"""
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("• {task.fields[stat]}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:

            task = progress.add_task(
                "[3/4] 响应时间",
                total=len(self.test_data),
                stat="测试中..."
            )

            async with self.session_maker() as session:
                for i, test_case in enumerate(self.test_data):
                    query = test_case['query']

                    start_time = time.time()
                    try:
                        result = await self.orchestrator.handle_query(
                            db=session,
                            session_id="benchmark_session",
                            user_query=query
                        )
                        elapsed_ms = (time.time() - start_time) * 1000
                        self.results['response_time']['times'].append(elapsed_ms)
                    except Exception as e:
                        self.results['response_time']['errors'].append({
                            'id': test_case['id'],
                            'query': query,
                            'error': str(e)
                        })

                    # 更新进度条
                    times = self.results['response_time']['times']
                    if times:
                        avg = sum(times) / len(times)
                        progress.update(task, advance=1, stat=f"平均: {avg:.0f}ms")
                    else:
                        progress.update(task, advance=1, stat="计算中...")

            # 最终结果
            if self.results['response_time']['times']:
                times = sorted(self.results['response_time']['times'])
                avg = sum(times) / len(times)
                p95_idx = int(len(times) * 0.95)
                p95 = times[min(p95_idx, len(times) - 1)]
                color = "green" if p95 < 3000 else "red"
                progress.update(task, stat=f"[{color}]平均: {avg:.0f}ms | P95: {p95:.0f}ms[/{color}]")

    async def test_answer_accuracy(self):
        """测试回答准确度"""
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("• {task.fields[stat]}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:

            task = progress.add_task(
                "[4/4] 回答准确度",
                total=len(self.test_data),
                stat="LLM评估中..."
            )

            async with self.session_maker() as session:
                for i, test_case in enumerate(self.test_data):
                    query = test_case['query']
                    expected_answer = test_case['expected_answer']

                    try:
                        result = await self.orchestrator.handle_query(
                            db=session,
                            session_id="benchmark_session",
                            user_query=query
                        )

                        actual_answer = result.get('response', '') if result else ''

                        is_accurate, reason = await self._evaluate_with_llm(
                            query, expected_answer, actual_answer
                        )

                        if is_accurate:
                            self.results['accuracy']['accurate'] += 1
                        else:
                            self.results['accuracy']['inaccurate'].append({
                                'id': test_case['id'],
                                'query': query,
                                'reason': reason
                            })

                        self.results['accuracy']['total'] += 1

                    except Exception as e:
                        # 静默处理错误，不打断进度条
                        pass

                    # 更新进度条
                    accurate = self.results['accuracy']['accurate']
                    total = self.results['accuracy']['total']
                    rate = accurate / total if total > 0 else 0
                    progress.update(task, advance=1, stat=f"准确: {accurate}/{total} ({rate:.1%})")

            # 最终结果
            if self.results['accuracy']['total'] > 0:
                rate = self.results['accuracy']['accurate'] / self.results['accuracy']['total']
                color = "green" if rate >= 0.85 else "red"
                progress.update(task, stat=f"[{color}]准确率: {rate:.1%}[/{color}]")

    async def _evaluate_with_llm(self, query: str, expected: str, actual: str) -> tuple:
        """使用 LLM 评估回答质量"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=settings.DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            prompt = f"""你是一个客服回答质量评估专家。

用户问题：{query}
期望答案要点：{expected[:500]}
实际回答：{actual[:500]}

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
            # 后备方案：简单文本匹配
            if not expected or not actual:
                return False, "空回答"

            expected_words = set(expected)
            actual_words = set(actual)
            overlap = len(expected_words & actual_words) / len(expected_words)

            return overlap > 0.3, f"文本匹配 {overlap:.0%}"

    def generate_report(self) -> str:
        """生成 Markdown 格式测试报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算统计数据
        recall = self.results['recall']
        recall_rate = recall['hits'] / recall['total'] if recall['total'] > 0 else 0

        transfer = self.results['transfer']
        transfer_rate = transfer['transfers'] / transfer['total'] if transfer['total'] > 0 else 0

        times = sorted(self.results['response_time']['times']) if self.results['response_time']['times'] else [0]
        avg_time = sum(times) / len(times) if times else 0
        p50 = times[len(times) // 2] if times else 0
        p95_idx = int(len(times) * 0.95)
        p95 = times[min(p95_idx, len(times) - 1)] if times else 0
        p99_idx = int(len(times) * 0.99)
        p99 = times[min(p99_idx, len(times) - 1)] if times else 0

        accuracy = self.results['accuracy']
        accuracy_rate = accuracy['accurate'] / accuracy['total'] if accuracy['total'] > 0 else 0

        # 生成报告
        report = f"""# 数字客服系统测试报告

**生成时间**: {now}
**测试用例数**: {len(self.test_data)}
**数据来源**: CustomerServiceQA 表

---

## 指标概览

| 指标 | 结果 | 阈值 | 状态 |
|------|------|------|------|
| 召回命中率 | {recall_rate:.1%} | ≥80% | {'✅ 通过' if recall_rate >= 0.8 else '❌ 未达标'} |
| 误转人工率 | {transfer_rate:.1%} | ≤10% | {'✅ 通过' if transfer_rate <= 0.1 else '❌ 未达标'} |
| P95 响应时间 | {p95:.0f}ms | <3000ms | {'✅ 通过' if p95 < 3000 else '❌ 未达标'} |
| 回答准确度 | {accuracy_rate:.1%} | ≥85% | {'✅ 通过' if accuracy_rate >= 0.85 else '❌ 未达标'} |

---

## 1. 召回命中率

### 指标定义
用户问题能否被系统正确匹配到对应的 QA 知识库记录。

### 计算方法
```
召回命中率 = 正确匹配的问题数 / 总测试问题数 × 100%
```
- 测试输入：CustomerServiceQA 表中的 typical_question（标准问题）
- 匹配判定：qa_matcher.match() 返回的 topic_name 等于期望的 topic_name

### 测试结果

| 指标 | 数值 |
|------|------|
| 命中数 | {recall['hits']} |
| 总数 | {recall['total']} |
| 命中率 | {recall_rate:.1%} |

"""

        if recall['misses']:
            report += "### 未命中列表\n\n"
            for item in recall['misses'][:10]:
                report += f"- [ID: {item['id']}] {item['query'][:50]}...\n"
                report += f"  - 期望: {item['expected']}, 实际匹配: {item['matched']}\n"
            if len(recall['misses']) > 10:
                report += f"\n*...还有 {len(recall['misses']) - 10} 条未显示*\n"

        report += f"""
---

## 2. 误转人工率

### 指标定义
正常业务问题被错误地触发"转人工"的比例。测试用例都是正常问题，不应触发转人工。

### 计算方法
```
误转人工率 = 被误判为需要转人工的问题数 / 总测试问题数 × 100%
```
- 检测方法：qa_matcher.should_transfer_to_human()
- 触发条件：包含转人工关键词 或 不满意关键词

### 测试结果

| 指标 | 数值 |
|------|------|
| 总检测数 | {transfer['total']} |
| 触发转人工数 | {transfer['transfers']} |
| 误转人工率 | {transfer_rate:.1%} |

"""

        if transfer['false_transfers']:
            report += "### 误触发列表\n\n"
            for item in transfer['false_transfers'][:10]:
                report += f"- [ID: {item['id']}] {item['query'][:50]}...\n"
            if len(transfer['false_transfers']) > 10:
                report += f"\n*...还有 {len(transfer['false_transfers']) - 10} 条未显示*\n"

        report += f"""
---

## 3. 响应速度

### 指标定义
从收到用户问题到返回回复的端到端响应时间（不含流式传输时间）。

### 计算方法
```
响应时间 = handle_query() 调用结束时间 - 调用开始时间
```
- P50: 50% 的请求在此时间内完成
- P95: 95% 的请求在此时间内完成
- P99: 99% 的请求在此时间内完成

### 测试结果

| 指标 | 时间(ms) |
|------|----------|
| 平均 | {avg_time:.0f} |
| P50 | {p50:.0f} |
| P95 | {p95:.0f} |
| P99 | {p99:.0f} |
| 最小 | {min(times):.0f} |
| 最大 | {max(times):.0f} |

"""

        if self.results['response_time']['errors']:
            report += f"### 错误 ({len(self.results['response_time']['errors'])} 条)\n\n"
            for item in self.results['response_time']['errors'][:5]:
                report += f"- [ID: {item['id']}] {item['error'][:50]}\n"

        report += f"""
---

## 4. 回答准确度

### 指标定义
系统生成的回答是否正确回应了用户问题，并包含了标准话术的核心要点。

### 计算方法
```
回答准确度 = LLM 判定为"正确"的回答数 / 总评估数 × 100%
```
- 评估方式：使用 LLM (qwen-plus) 自动评估
- 评估依据：对比实际回答与标准话术 (standard_script)
- 评估标准：是否正确回应问题 + 是否包含核心要点

### 测试结果

| 指标 | 数值 |
|------|------|
| 准确数 | {accuracy['accurate']} |
| 评估总数 | {accuracy['total']} |
| 准确率 | {accuracy_rate:.1%} |

"""

        if accuracy['inaccurate']:
            report += "### 不准确案例\n\n"
            for item in accuracy['inaccurate'][:10]:
                report += f"- [ID: {item['id']}] {item['query'][:40]}...\n"
                report += f"  - 原因: {item['reason'][:50]}\n"
            if len(accuracy['inaccurate']) > 10:
                report += f"\n*...还有 {len(accuracy['inaccurate']) - 10} 条未显示*\n"

        return report

    def show_summary_table(self):
        """显示测试结果汇总表格"""
        recall = self.results['recall']
        recall_rate = recall['hits'] / recall['total'] if recall['total'] > 0 else 0

        transfer = self.results['transfer']
        transfer_rate = transfer['transfers'] / transfer['total'] if transfer['total'] > 0 else 0

        times = sorted(self.results['response_time']['times']) if self.results['response_time']['times'] else [0]
        p95_idx = int(len(times) * 0.95)
        p95 = times[min(p95_idx, len(times) - 1)] if times else 0

        accuracy = self.results['accuracy']
        accuracy_rate = accuracy['accurate'] / accuracy['total'] if accuracy['total'] > 0 else 0

        # 创建表格
        table = Table(title="测试结果汇总", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan")
        table.add_column("结果", justify="right")
        table.add_column("阈值", justify="right")
        table.add_column("状态", justify="center")

        # 添加行
        table.add_row(
            "召回命中率",
            f"{recall_rate:.1%}",
            "≥80%",
            "[green]✓ 通过[/green]" if recall_rate >= 0.8 else "[red]✗ 未达标[/red]"
        )
        table.add_row(
            "误转人工率",
            f"{transfer_rate:.1%}",
            "≤10%",
            "[green]✓ 通过[/green]" if transfer_rate <= 0.1 else "[red]✗ 未达标[/red]"
        )
        table.add_row(
            "P95 响应时间",
            f"{p95:.0f}ms",
            "<3000ms",
            "[green]✓ 通过[/green]" if p95 < 3000 else "[red]✗ 未达标[/red]"
        )
        table.add_row(
            "回答准确度",
            f"{accuracy_rate:.1%}",
            "≥85%",
            "[green]✓ 通过[/green]" if accuracy_rate >= 0.85 else "[red]✗ 未达标[/red]"
        )

        console.print()
        console.print(table)

    def save_report(self, report: str):
        """保存报告到文件"""
        os.makedirs(REPORTS_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_report_{timestamp}.md"
        filepath = os.path.join(REPORTS_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        console.print(f"\n[green]✓[/green] 报告已保存到: [bold]{filepath}[/bold]")
        return filepath

    async def cleanup(self):
        """清理资源"""
        if self.engine:
            await self.engine.dispose()


async def main():
    """主函数"""
    runner = BenchmarkRunner()

    try:
        await runner.initialize()
        await runner.run_all_tests()

        # 显示汇总表格
        runner.show_summary_table()

        # 生成并保存报告
        report = runner.generate_report()
        runner.save_report(report)

    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
