# Image

根据文本提示、尺寸等信息，使用文心一格大模型，自动创作图片。

## 函数接口

``` {.py .copy}
erniebot.Image.create(**kwargs: Any) -> EBResponse:
```
## 输入参数

调用Image接口前，大家需要首先设置`api_type`参数。

``` {.py .copy}
ernie.api_type = 'yinian'
```

`erniebot.Image.create` 接口的详细参数如下：

| 参数名 | 类型     | 必填    | 描述   |
| :-----| :-----  | :----- | :----- |
| model | string  | 是 | 模型名称。支持`ernie-vilg-v2`。|
| version | string | 否 | 模型版本。支持 v1、v2，默认为v2。v2 为最新模型，比 v1 在准确度、精细度上有比较明显的提升，且 v2 支持更多尺寸。 |
| prompt | string | 是 | 生图的文本描述。仅支持中文、日常标点符号。不支持英文，特殊符号，限制 200 字。 |
| width | int     | 是 | 图片宽度。v1 版本支持：1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560；v2 版本支持：512x512、640x360、360x640、1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560 |
| height | int     | 是 | 图片高度。v1 版本支持：1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560；v2 版本支持：512x512、640x360、360x640、1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560 |
| image_num | int | 否 | 生成图片数量。默认一张，支持生成 1-8 张。 |


## 返回结果

`erniebot.Image.create` 接口返回的示例数据如下：

```
{
   "data": {
     "task_id": 1659384536691865192,
     "task_status": "SUCCESS",
     "task_progress": 1
     "sub_task_result_list": [
        {
          "sub_task_status": "SUCCESS",
          "sub_task_progress": 1,
          "sub_task_error_code": 0,
          "final_image_list": [
           {  
              "img_url": "http://aigc-t2p.bj.bcebos.com/artist-long/_final.png?02d252c87b91ed3b2f6327db0",
              "width": 512,
              "height": 512,
              "img_approve_conclusion": "pass"
            }
        ]
      }
    ]
  }
}
```

返回结果的具体字段含义如下表：

| 字段  | 类型   | 描述  |
| :--- | :---- | :---- |
| data | object | 返回数据 |
| task_id | int | 任务ID |
| task_status | string | 任务总体状态，有INIT（初始化）、WAIT（排队中）、RUNNING（生成中）、FAILED（失败）、SUCCESS（成功）五种状态，只有 SUCCESS 为成功状态 |
| task_progress | int | 任务总体进度，0表示未处理完，1表示处理完成 |
| sub_task_result_list | object[] | 子任务的结果列表 |
| sub_task_status | string | 子任务状态，有INIT（初始化）、WAIT（排队中）、RUNNING（生成中）、FAILED（失败）、SUCCESS（成功）五种状态，只有 SUCCESS 为成功状态 |
| sub_task_progress | int | 子任务进度，0表示未处理完，1表示处理完成 |
| sub_task_error_code | int | 子任务任务错误码，0表示正常，501表示文本黄反拦截，201表示模型生图失败 |
| final_image_list | object[] | 子任务生成图像的列表 |
| img_url | string | 图片的下载地址，默认 1 小时后失效 |
| height | int | 图片的高度 |
| width | int | 图片的宽度 |
| img_approve_conclusion | string | 图片机审结果，"block"表示输出图片违规，"review"表示输出图片疑似违规，"pass"表示输出图片未发现问题|


## 使用示例

``` {.py .copy}
import erniebot

# erniebot.ak = "<EB-ACCESS-KEY-ID>"
# erniebot.sk = "<EB-SECRET-ACCESS-KEY>"

erniebot.api_type = "yinian"

response = erniebot.Image.create(model='ernie-vilg-v2', prompt='请帮我画一只可爱的大猫咪', width=512, height=512, version='v2', image_num=1)

print(response)
```
