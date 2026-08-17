"""
python scripts/spider/xudaxian/xudaxain_spider.py \
  --url https://www.yuque.com/fairy-era/yg511q/ \
  --import-db \
  --knowledge-base-id 44 \
  --author-id 15 \
  --image-obs-prefix wiki/yuque/xudaxian \
  -o yuque_xudaxian_import.json







python scripts/spider/xudaxian/xudaxain_spider.py \
  --url https://www.yuque.com/fairy-era/yg511q/ \
  --import-db \
  --knowledge-base-id 44 \
  --author-id 15 \
  --image-obs-prefix wiki/yuque/xud \
  --limit 3  \
  --no-migrate-images \
  -o yuque_test.json



error:
处理图片/Quill [60/278] 第一章：基本概念（了解）
    失败: HTTP Error 403: Forbidden


处理图片/Quill [215/278] 1 主从复制
    失败: unknown url type: 'images/通过 redis-check-rdb 命令可以查看该信息.png'


处理图片/Quill [267/278] 1 引入
    失败: unknown url type: 'images/创建一个Helm Chart应用示例之创建Chart.png'

处理图片/Quill [275/278] 1 Jenkins+Docker+SpringCloud持续集成说明
/root/code/wiki-zs/wiki-backend/scripts/spider/xiaolincoding/markdown_quill.py:329: FutureWarning: The behavior of this method will change in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
  pre = _find_pre_in_code_wrapper(child) or child









"""