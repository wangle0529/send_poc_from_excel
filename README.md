# 使用指南

`send_poc_from_excel` 是一个命令行工具，用于从Excel文件中读取POC（概念验证）数据，并将这些数据发送到指定的目标地址（dst），然后将响应结果写回到一个新的Excel文件中。此工具主要用于测试服务器响应情况和WAF防护效果。

## 用法

```shell
send_poc_from_excel.exe [-h] --input_file INPUT_FILE --row ROW --column COLUMN --output_file OUTPUT_FILE --output_column OUTPUT_COLUMN --dst DST
```
## 示例
```shell
.\send_poc_from_excel.exe --input_file D:\testfiles\123.xlsx --row 2 --column 2 --output_file D:\testfiles\789.xlsx --output_column 6 --dst 192.168.1.200:8080
```

## 图形化界面，支持发送单条报文和批量发送
<img width="766" height="606" alt="image" src="https://github.com/user-attachments/assets/543bee90-f882-4c58-83f0-bffbfeef9fa0" />

<img width="768" height="607" alt="image" src="https://github.com/user-attachments/assets/9d1b5699-6a20-439d-aaec-5bcf02891604" />

