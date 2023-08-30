# Embedding

Embedding可以将文本转化为用数值表示的向量形式，用于文本检索、信息推荐、知识挖掘等场景。

## 函数接口

``` {.py .copy}
erniebot.Embedding.create(**kwargs: Any)
	-> Union[EBResponse, Iterator[EBResponse]]
```

## 输入参数

| 参数名 | 类型 | 必填 | 描述 |
| :---   | :--- | :------- | :---- |
| model  | string | 是 | 模型名，支持"ernie-text-embedding" |
| input | list(string) | 是 | 输入的文本列表，服务可以支持计算多段文本的向量，列表中每个元素即为一段单独的文本。注意， <br>(1) 列表长度不要超过16 <br>(2) 服务在计算向量时，每段文本只支持最多384个Token, 超长报错。服务采用汉字数 + 单词数 * 1.3估算Token数量 <br>(3) 文本内容不能为空 |
| user_id | string | 否 | 表示最终用户的唯一标识符，可以监视和检测滥用行为，防止接口恶意调用 |


## 返回结果

接口返回`erniebot.response.EBResponse`结构体。

`erniebot.response.EBResponse`结构体示例数据如下所示：
```
{
    "code": 200,
    "id": "as-s0tdsgnuu4",
    "object": "embedding_list",
    "created": 1692933427,
    "data": [
        {
            "object": "embedding",
            "embedding": [
                0.12393086403608322,
                0.06512520462274551,
                0.05346716567873955,
                ...
            ],
            "index": 0
        },
        {
            "object": "embedding",
            "embedding": [
                0.12393086403608322,
                0.06512520462274551,
                0.05346716567873955,
                ...
            ],
            "index": 1
        }
    ],
    "usage": {
        "prompt_tokens": 98,
        "total_tokens": 98
    }
}
```

其中字段含义如下表所示：

| 字段 | 类型 | 描述 |
| :--- | :---- | :---- |
| code | int | 请求返回状态 |
| data | list(dict) | 向量计算结果，列表中元素个数与输入的文本个数一致。各元素为一个dict结构，分别表示, <br>object(string): 固定为"embedding" <br>embedding(list of float): 384维的向量结果 <br>index: 序号 |
| usage | dict | 输入输出Token统计信息，注意当前Token统计采用估算逻辑， token数 = 汉字数 + 单词数 * 1.3。<br>prompt_tokens/total_tokens(int): 输入Token数量 |

## 使用示例

``` {.py .copy}
import erniebot
import numpy as np

# erniebot.ak = "<EB-ACCESS-KEY-ID>"
# erniebot.sk = "<EB-SECRET-ACCESS-KEY>"

embedding_response = erniebot.Embedding.create(
    model="ernie-text-embedding",
    input=[
        "我是百度公司开发的人工智能语言模型，我的中文名是文心一言，英文名是ERNIE-Bot，可以协助您完成范围广泛的任务并提供有关各种主题的信息，比如回答问题，提供定义和解释及建议。如果您有任何问题，请随时向我提问。",
        "2018年深圳市各区GDP"
    ])

for emb_res in embedding_response.data:
    embedding = np.array(emb_res["embedding"])
    print(embedding)
```
