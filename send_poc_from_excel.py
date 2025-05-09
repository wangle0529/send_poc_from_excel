from urllib.parse import unquote
from openpyxl import load_workbook
from urllib.parse import urlencode
import time
import argparse
import json
import requests
import re

class excel_sender:

    def __init__(self,input_file,row,column,output_file,output_column,dst):
        self.input_file=input_file
        self.row=row
        self.column=column
        self.output_file=output_file
        self.output_column=output_column
        self.dst=dst



    def parse(self,raw_request):
        #解析一条poc
        # 解码URL编码的字符
        # decoded_request = unquote(raw_request)
        decoded_request = raw_request

        # 分离请求头和请求体
        header_body_split = decoded_request.split(
            '\r\n\r\n') if '\r\n\r\n' in decoded_request else decoded_request.split('\n\n')
        headers_str = header_body_split[0]
        body_str = ""


        for i in range(len(header_body_split)):
            if i>0:
                body_str=body_str+"\n"+header_body_split[i]     #增加请求体多个空行处理，v1.1


        # print(headers_str)
        # print(body_str)

        # 解析请求头
        self.headers = {}
        self.body=""
        self.method=""
        self.path=""
        for line in headers_str.splitlines():
            if ': ' in line:
                key, value = line.split(': ', 1)
                self.headers[key] = value
            elif re.match(r'.*:$', line) :        #处理请求头没有value,v1.2
                # print(line)
                key,value= line.split(':',1)
                # print(key)
                self.headers[key] = value
            else:
                # first_line=line
                # print(len(line))
                self.method=line.split(" ")[0]
                self.path=line.split(" ")[1]

        # 解析请求体
        # 注意：这里假设请求体是JSON或类似结构化的数据，如果不是，则需要根据实际格式调整解析方法
        # try:
        #     self.body = json.loads(body_str)
        # except json.JSONDecodeError:
        #     # 如果不是JSON格式，直接使用原始字符串
        #     self.body = body_str
        self.body = body_str
        # 输出解析结果
        # print("Headers:")
        # print(self.headers)
        # print("Body:")
        # print(self.body)
        #
        # print(self.method)
        # print(self.path)

    def send_1_poc(self):
        #发送一条poc
        self.return_content=""
        response = requests.post(
            url=f"http://{self.dst}{self.path}",
            headers=self.headers,
            data=self.body
        )

        return response


    def read_excel(self):

        file_path = self.input_file  # 替换为你的Excel文件路径
        output_file_path = self.output_file
        sheet_name = 'Sheet1'  # 替换为你想要读取的工作表名称

        wb = load_workbook(filename=file_path)
        ws = wb[sheet_name]

        # 定义遍历的行范围
        start_row = self.row  # 开始行（包含），基于1索引
        col=self.column   #报文所在列
        col1=self.output_column    #输出的列，

        # 获取最大行号
        max_row = ws.max_row


        for row in ws.iter_rows(min_row=start_row, max_row=max_row,  min_col=col, max_col=col,values_only=True):
            if any(cell is not None for cell in row):  # 检查行是否包含非空单元格
                tmp_row=row[0]
                # print("Row:", tmp_row)
                self.parse(tmp_row)
                try:             # v1.4,异常退出并报错
                    response_all=self.send_1_poc()
                except Exception as e:
                    print("第" + str(start_row) + "行发送异常，请检查后重新发送！")
                    break


                ws.cell(row=start_row, column=col1, value=response_all.text)

                ws.cell(row=start_row,column=col1+1,value=response_all.status_code)

                pattern_ah = r"Request ID:  (\d{19})"
                pattern_ct = r"event_id: ([a-fA-F0-9]{32})"              #v1.3,ct返回id
                match_ah = re.search(pattern_ah, response_all.text)
                if match_ah:
                    ws.cell(row=start_row, column=col1+2, value=match_ah.group(1))

                match_ct = re.search(pattern_ct, response_all.text)
                if match_ct:
                    ws.cell(row=start_row, column=col1 + 2, value=match_ct.group(1))

                wb.save(output_file_path)
            print("第"+str(start_row)+"行发送完成！")      #v1.4，打印行号
            start_row += 1
            time.sleep(0.2)

        wb.save(output_file_path)

def main():

    parser = argparse.ArgumentParser(description='POC批量发送')
    parser.add_argument('--input_file', type=str, help='输入文件',required=True)
    parser.add_argument('--row', type=int, help='第一个报文所在行号',required=True)
    parser.add_argument('--column', type=int, help='报文所在列号',required=True)
    parser.add_argument('--output_file', type=str, help='输出文件', required=True)
    parser.add_argument('--output_column', type=int, help='响应内容、状态码、Request ID，输出三列', required=True)
    parser.add_argument('--dst', type=str, help='站点地址，ip:port，不支持https', required=True)

    args = parser.parse_args()
    input_file=args.input_file
    row=args.row
    column=args.column
    output_file=args.output_file
    output_column=args.output_column
    dst=args.dst


    test=excel_sender(input_file,row,column,output_file,output_column,dst)
    print("检测中，请稍候......")
    test.read_excel()
    print("检测完成！")



if __name__ == '__main__':
    main()
