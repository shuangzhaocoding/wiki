"""
# 基础教程
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_primary/python_primary_tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1098 \
  --image-obs-prefix wiki/coolpython/python_basic_tutorial \
  -o python_basic_tutorial_import.json

# 进阶教程
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_senior/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1304 \
  --image-obs-prefix wiki/coolpython/python_senior_tutorial \
  -o python_senior_tutorial_import.json
error:
  处理图片/Quill [117/199] requests快速入门
    失败: HTTP Error 403: Forbidden
  处理图片/Quill [189/199] python实战练手项目---下载文件并添加进度条
    失败: HTTP Error 404: Not Found

# 编程思维
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_programming_thinking/what_is_programming_thinking.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1307 \
  --image-obs-prefix wiki/coolpython/python_programming_thinking \
  -o python_programming_thinking_import.json


# 设计模式
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/design_mode/create/single_pattern.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1308 \
  --image-obs-prefix wiki/coolpython/python_design_mode \
  -o python_design_mode_import.json

# 小项目实战
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_little_pro/base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1518 \
  --image-obs-prefix wiki/coolpython/python_little_pro \
  -o python_little_pro_import.json

# http协议
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/http_protocol/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1566 \
  --image-obs-prefix wiki/coolpython/python_http_protocol \
  -o python_http_protocol_import.json

# flask
http://coolpython.net/flask_tutorial/index.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/flask_tutorial/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1567 \
  --image-obs-prefix wiki/coolpython/python_flask \
  -o python_flask_import.json
  
# tornado
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/tornado/tornado_base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1568 \
  --image-obs-prefix wiki/coolpython/tornado_base \
  -o python_tornado_import.json

# fastapi
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/fastapi/fastapi_base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1569 \
  --image-obs-prefix wiki/coolpython/fastapi \
  -o python_fastapi_import.json


# redis http://coolpython.net/python_db/redis/python_redis_tutorial.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_db/redis/python_redis_tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1654 \
  --image-obs-prefix wiki/coolpython/python_redis \
  -o python_redis_import.json

# mysql http://coolpython.net/python_db/python_mysql_tutorial.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_db/python_mysql_tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1655 \
  --image-obs-prefix wiki/coolpython/python_mysql \
  -o python_mysql_import.json

# mongo http://coolpython.net/python_db/python-mongo-tutorial.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_db/python-mongo-tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1656 \
  --image-obs-prefix wiki/coolpython/python_mongo \
  -o python_mongo_import.json

# http://coolpython.net/data_analysis/pandas/pandas_base.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/data_analysis/pandas/pandas_base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1687 \
  --image-obs-prefix wiki/coolpython/python_pandas \
  -o python_pandas_import.json

# http://coolpython.net/data_analysis/numpy/numpy_tutorial.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/data_analysis/numpy/numpy_tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1688 \
  --image-obs-prefix wiki/coolpython/python_numpy \
  -o python_numpy_import.json

# http://coolpython.net/data_analysis/matplotlib/matplotlib_tutorial.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/data_analysis/matplotlib/matplotlib_tutorial.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1689 \
  --image-obs-prefix wiki/coolpython/python_matplotlib \
  -o python_matplotlib_import.json

# http://coolpython.net/data_analysis/excel/openpyxl-index.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/data_analysis/excel/openpyxl-index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1690 \
  --image-obs-prefix wiki/coolpython/python_openpyxl \
  -o python_openpyxl_import.json

# http://coolpython.net/tk/tk_primary/index.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/tk/tk_primary/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1760 \
  --image-obs-prefix wiki/coolpython/python_tk \
  -o python_tk_import.json

# http://coolpython.net/informal_essay/index.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/informal_essay/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1785 \
  --image-obs-prefix wiki/coolpython/python_informal_essay \
  -o python_informal_essay_import.json

# http://coolpython.net/pysrc/littlepro/base.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/pysrc/littlepro/base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1787 \
  --image-obs-prefix wiki/coolpython/python_little_pro \
  -o python_little_pro_import.json

# http://coolpython.net/pysrc/framework/base.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/pysrc/framework/base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1788 \
  --image-obs-prefix wiki/coolpython/python_framework \
  -o python_framework_import.json

# http://coolpython.net/python_interview/base.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/python_interview/base.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1927 \
  --image-obs-prefix wiki/coolpython/python_python_interview \
  -o python_python_interview_import.json

# http://coolpython.net/py_answer/index.html
python scripts/spider/coolpython/coolpython_spider.py \
  --url http://coolpython.net/py_answer/index.html \
  --import-db \
  --knowledge-base-id 39 \
  --author-id 15 \
  --parent-id 1928 \
  --image-obs-prefix wiki/coolpython/python_py_answer \
  -o python_py_answer_import.json
"""