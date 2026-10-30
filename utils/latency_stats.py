import math


class LatencyStats:
    """延时统计工具

    记录每次请求的耗时（毫秒），并输出平均值、最小值、最大值、P50、P95 等统计指标。
    失败请求（status_code 为 0）单独计数，不参与延时分布计算。
    """

    # 记录条数上限，避免长时间循环发送导致内存无限增长
    MAX_RECORDS = 100000

    def __init__(self):
        self.reset()

    def reset(self):
        """清空所有统计"""
        self.records = []
        self.fail_count = 0

    def add(self, elapsed_ms, success=True):
        """记录一次请求耗时

        :param elapsed_ms: 耗时（毫秒），None 表示未取到
        :param success: 请求是否成功（状态码非 0）
        """
        if elapsed_ms is None:
            return
        if success:
            if len(self.records) < self.MAX_RECORDS:
                self.records.append(elapsed_ms)
        else:
            self.fail_count += 1

    @property
    def count(self):
        """总请求数"""
        return len(self.records) + self.fail_count

    @property
    def success_count(self):
        """成功请求数"""
        return len(self.records)

    @property
    def avg(self):
        if not self.records:
            return 0.0
        return sum(self.records) / len(self.records)

    @property
    def min(self):
        if not self.records:
            return 0.0
        return min(self.records)

    @property
    def max(self):
        if not self.records:
            return 0.0
        return max(self.records)

    def percentile(self, p):
        """计算百分位数，如 percentile(95) 即 P95"""
        if not self.records:
            return 0.0
        ordered = sorted(self.records)
        idx = max(0, math.ceil(p / 100.0 * len(ordered)) - 1)
        return ordered[idx]

    @property
    def p50(self):
        return self.percentile(50)

    @property
    def p95(self):
        return self.percentile(95)

    def summary(self, title="=== 延时统计 ==="):
        """生成多行统计汇总文本"""
        if self.count == 0:
            return f"{title}\n暂无数据"

        lines = [
            title,
            f"总请求: {self.count}   成功: {self.success_count}   失败: {self.fail_count}",
        ]
        if self.records:
            lines.append(
                f"平均: {self.avg:.2f}ms  最小: {self.min:.2f}ms  最大: {self.max:.2f}ms  "
                f"P50: {self.p50:.2f}ms  P95: {self.p95:.2f}ms"
            )
        return "\n".join(lines)
