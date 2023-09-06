# 参数配置

ERNIE Bot SDK参数配置，主要涉及认证鉴权、后端平台等信息。

ERNIE Bot SDK支持3种参数配置的方法：1）使用环境变量，2）使用全局变量，3) 使用`_config_`参数。

1. 使用环境变量：

``` {.copy}
export EB_API_TYPE="<EB-API-TYPE>"
```

2. 使用全局变量：

``` {.py .copy}
import erniebot
erniebot.api_type = "<EB-API-TYPE>"
```

3. 使用`_config_`参数：

``` {.py .copy}
import erniebot

response = erniebot.ChatCompletion.create(
    _config_=dict(
        api_type="<EB-API-TYPE>",
    ),
    model="ernie-bot-3.5",
    messages=[{
        "role": "user",
        "content": "你好，请介绍下你自己",
    }],
)
```

注意：允许同时使用多种方式设置鉴权信息，程序将根据设置方式的优先级确定配置项的最终取值。三种设置方式的优先级从高到低依次为：使用`_config_`参数，使用全局变量，使用环境变量。

ERNIE Bot SDK支持的参数，具体介绍如下：

| API参数名称   | 环境变量名称  |  类型   |  必须设置 |  描述   |
| :---         | :----       | :----  | :---- |  :---- |
| api_type     | EB_API_TYPE | string | 否 | 设置后端平台的类型。支持`'qianfan'`和`'yinian'`，默认是`'qianfan'`。|
| ak           | EB_AK       | string | 否 | 设置认证鉴权的access key。必须和`sk`同时设置。 |
| sk           | EB_SK       | string | 否 | 设置认证鉴权的secret key。必须和`ak`同时设置。 |
| access_token | EB_ACCESS_TOKEN | string | 否 | 设置认证鉴权的access token。推荐优先使用`ak`和`sk`。如果设置了`access_token`，则使用该access token；如果`access_token`没有设置或者失效，并且设置了`ak`和`sk`，部分后端平台类型支持自动通过`ak`和`sk`获取access token。|
| access_token_path | EB_ACCESS_TOKEN_PATH | string | 否 | 设置存有access token的文件路径。推荐优先使用`ak`和`sk`。`access_token_path`生效原理和`access_token`相同。|
| proxy        | EB_PROXY    | string | 否 | 设置请求的代理 。|
| timeout      | EB_TIMEOUT  | float  | 否 | 设置请求超时的时间。如果设置了`timeout`，请求失败后会再次请求，直到成功或者超过设置的时间。|
