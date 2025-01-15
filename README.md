# send_poc_from_excel
send_poc_from_excel


usage: send_poc_from_excel.exe [-h] --input_file INPUT_FILE --row ROW --column COLUMN --output_file OUTPUT_FILE --output_column OUTPUT_COLUMN --dst DST

POC批量发送

options:
  -h, --help            show this help message and exit
  --input_file INPUT_FILE
                        输入文件
  --row ROW             第一个报文所在行号
  --column COLUMN       报文所在列号
  --output_file OUTPUT_FILE
                        输出文件
  --output_column OUTPUT_COLUMN
                        响应内容、状态码、request ID，输出三列
  --dst DST             站点地址，ip:port，不支持https


example：
    .\send_poc_from_excel.exe --input_file D:\VM\python\POC\venv\Files\123.xlsx --row 2 --column 2 --output_file D:\VM\python\POC\venv\Files\789.xlsx --output_column 6 --dst 10.50.81.59:8000




changelog：
v1.1：
  1、增加了报文中多个空行的处理
  
v1.2：
  1、增加了请求头值为空的处理