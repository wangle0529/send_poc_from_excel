# send_poc_from_excel 使用指南

`send_poc_from_excel` 是一个命令行工具，用于从Excel文件中读取POC（概念验证）数据，并将这些数据发送到指定的目标地址（dst），然后将响应结果写回到一个新的或现有的Excel文件中。此工具主要用于测试或者与Web服务进行交互。

## 用法

```shell
send_poc_from_excel.exe [-h] --input_file INPUT_FILE --row ROW --column COLUMN --output_file OUTPUT_FILE --output_column OUTPUT_COLUMN --dst DST
```
## 示例
```shell
.\send_poc_from_excel.exe --input_file D:\VM\python\POC\venv\Files\123.xlsx --row 2 --column 2 --output_file D:\VM\python\POC\venv\Files\789.xlsx --output_column 6 --dst 10.50.81.59:8000
```
