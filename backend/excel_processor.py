import time
import re
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from .http_client import HTTPClient
from .request_parser import RequestParser
from utils.latency_stats import LatencyStats

class ExcelProcessor:
    """Excel 文件处理器"""
    
    def __init__(self, input_file, row, column, output_file, output_column, dst, use_https, 
                 auto_update_content_length='n', send_only=0, loop=0, log_func=None, finish_callback=None, send_interval=0.1,
                 record_latency=1):
        self.input_file = input_file
        self.row = row
        self.column = column
        self.output_file = output_file
        self.output_column = output_column
        self.dst = dst
        self.use_https = use_https
        self.auto_update_content_length = auto_update_content_length
        self.send_only = send_only
        self.loop = loop
        self.log = log_func if log_func else print
        self.finish = finish_callback if finish_callback else lambda: None
        self.send_interval = send_interval
        self.stop_flag = False
        # 延时统计：record_latency=1 时把耗时写入【输出列+3】
        self.record_latency = record_latency
        self.stats = LatencyStats()
        
        self.http_client = HTTPClient()
        self.parser = RequestParser()
    
    def stop(self):
        """停止处理"""
        self.stop_flag = True
    
    def _process_one_round(self, ws, ws1, col, col1):
        """处理一轮（从起始行到最后一行）"""
        start_row = self.row
        max_row = ws.max_row

        for row in ws.iter_rows(min_row=start_row, max_row=max_row, 
                               min_col=col, max_col=col, values_only=True):
            if self.stop_flag:
                self.log("处理已停止")
                break

            if any(cell is not None for cell in row):
                tmp_row = row[0]
                try:
                    # 解析请求
                    request_data = self.parser.parse(tmp_row)

                    # 构建 URL
                    if self.use_https in ['yes', 'y', 'Yes', 'Y']:
                        url = f"https://{self.dst}{request_data['path']}"
                    else:
                        url = f"http://{self.dst}{request_data['path']}"

                    # 自动更新 Content-Length
                    if self.auto_update_content_length in ['yes', 'y', 'Yes', 'Y']:
                        body_length = len(request_data['body']) if request_data['body'] else 0
                        headers = request_data['headers']
                        has_content_length = any(key.lower() == 'content-length' for key in headers)
                        if has_content_length:
                            keys_to_delete = [key for key in headers if key.lower() == 'content-length']
                            for key in keys_to_delete:
                                del headers[key]
                        if body_length > 0:
                            headers.add('Content-Length', str(body_length))

                    # 发送请求
                    response = self.http_client.send_request(
                        method=request_data['method'],
                        url=url,
                        headers=request_data['headers'],
                        body=request_data['body'],
                        http_version=request_data['http_version']
                    )

                    # 延时统计：记录本次请求耗时
                    elapsed_ms = getattr(response, 'elapsed_ms', None)
                    ttfb_ms = getattr(response, 'ttfb_ms', None)
                    self.stats.add(elapsed_ms, success=(getattr(response, 'status_code', 0) != 0))

                    if not self.send_only and ws1 is not None:
                        # 写入响应
                        ws1.cell(row=start_row, column=col1, value=response.text)
                        ws1.cell(row=start_row, column=col1+1, value=response.status_code)

                        # 写入耗时（毫秒，位于【输出列+3】）
                        if self.record_latency:
                            ws1.cell(row=start_row, column=col1+3,
                                     value=round(elapsed_ms, 2) if elapsed_ms is not None else None)

                        # 提取 Request ID
                        pattern_ah = r"Request ID:\s*(\d{19})"
                        pattern_ct = r"event_id:\s*([a-fA-F0-9]{32})"
                        match_ah = re.search(pattern_ah, response.text)
                        if match_ah:
                            ws1.cell(row=start_row, column=col1+2, value=match_ah.group(1))

                        match_ct = re.search(pattern_ct, response.text)
                        if match_ct:
                            ws1.cell(row=start_row, column=col1+2, value=match_ct.group(1))

                    cost_text = f"{elapsed_ms:.2f}ms" if elapsed_ms is not None else "-"
                    ttfb_text = f"{ttfb_ms:.2f}ms" if ttfb_ms is not None else "-"
                    self.log(f"第{start_row}行发送完成，响应码：{response.status_code}，"
                             f"耗时：{cost_text}（首字节 {ttfb_text}）")
                except Exception as e:
                    self.log(f"第{start_row}行处理失败：{str(e)}")
                    if not self.send_only and ws1 is not None:
                        ws1.cell(row=start_row, column=col1, value=f"处理失败：{str(e)}")
                        ws1.cell(row=start_row, column=col1+1, value=0)

            start_row += 1
            time.sleep(self.send_interval)

    def process(self):
        """处理 Excel 文件并发送请求"""
        try:
            # 加载 Excel 文件
            wb = load_workbook(filename=self.input_file)
            ws = wb['Sheet1']

            # 处理输出文件（仅发送模式下跳过）
            wb1 = None
            ws1 = None
            if not self.send_only:
                try:
                    wb1 = load_workbook(self.output_file)
                except FileNotFoundError:
                    wb1 = wb
                ws1 = wb1.active

            col = self.column
            col1 = self.output_column

            # 循环发送模式
            if self.loop:
                loop_count = 0
                while not self.stop_flag:
                    loop_count += 1
                    self.log(f"--- 第 {loop_count} 轮循环发送开始 ---")
                    self._process_one_round(ws, ws1, col, col1)
                self.log(f"循环已停止，共发送 {loop_count} 轮")
            else:
                self._process_one_round(ws, ws1, col, col1)

            # 保存结果（仅发送模式下跳过）
            if not self.send_only and wb1 is not None:
                # 写入耗时列表头（起始行大于 1 时，第 1 行视为表头行）
                if self.record_latency and self.row > 1:
                    ws1.cell(row=1, column=col1+3, value="耗时(ms)")
                ws1.column_dimensions[get_column_letter(col)].width = 100
                wb1.save(self.output_file)

            # 输出延时统计汇总
            if self.stats.count:
                self.log("")
                self.log(self.stats.summary())
        except Exception as e:
            self.log(f"发生错误: {e}")
        finally:
            self.finish()