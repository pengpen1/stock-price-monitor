# V1.2.1项目迭代计划

#### 稳定版本V1.2.1的思考

- [ ] 更新版本，新接口一定要兼容旧数据，不能让用户更新次版本，直接把数据清空了

  1）增加版本类型，patch、minor、major

  2）尝试采用本地数据 schema + migration 规范，只做 **增量迁移**，用户数据>新功能，如果新功能不能兼容旧数据，需要提示用户，是否覆盖升级

- [ ] 当前Mac系统下载[.dmg](https://github.com/pengpen1/stock-price-monitor/releases/download/v1.2.0/-1.2.0-arm64.dmg)并进行安装发现安装失败，报错为不支持打开.app后缀的应用程序，估计需要调整下相关打包配置（window是正常的）

- [x] 支持更多国产模型，如比较火的豆包、GLM、千问、kimi、DeepSeek（后端协议抽象已完成）

  ```
  ├── OpenAI Compatible（兼容规范）
  │   ├── OpenAI 官方
  │   ├── Azure OpenAI
  │   ├── DeepSeek
  │   ├── 月之暗面 Kimi
  │   ├── 通义千问（兼容模式）
  │   ├── Grok（部分接口）
  │
  ├── Google Gemini Native
  ├── Anthropic Native
  ├── 字节豆包 Native
  ├── 智谱 GLM Native
  ---
  先统一「能力抽象」，不要从厂商入手，以「协议 / API 规范」为第一维度
  后端统一配置结构
  例子：class ProviderConfig(BaseModel):
      id: str                  # openai / deepseek / kimi
      label: str               # UI 显示名
      protocol: str            # openai | gemini | anthropic | custom
      base_url: str | None     # OpenAI-compatible 必填
      auth_type: str           # bearer | api-key | custom-header
      key_prefix: str | None   # sk- / sk-ant- / 可选
      models_endpoint: str     # /v1/models
  {
    "id": "deepseek",
    "label": "DeepSeek",
    "protocol": "openai",
    "base_url": "https://api.deepseek.com",
    "auth_type": "bearer",
    "key_prefix": "sk-",
    "models_endpoint": "/v1/models"
  }
  PROTOCOL_MAP = {
      "openai": OpenAICompatibleProtocol(),
      "gemini": GeminiProtocol(),
      "anthropic": ClaudeProtocol(),
      "doubao": DoubaoProtocol(),
      "glm": GLMProtocol(),
  }
  def get_models(provider_id, api_key, proxy):
      config = PROVIDER_REGISTRY[provider_id]
      protocol = PROTOCOL_MAP[config.protocol]
      return protocol.get_models(config, api_key, proxy)
  ---
  最后才是厂商list:
  例如：[
    {
      "id": "openai",
      "label": "OpenAI (GPT)",
      "protocol": "openai",
      "needProxy": true,
      "keyPlaceholder": "sk-..."
    },
    {
      "id": "deepseek",
      "label": "DeepSeek",
      "protocol": "openai",
      "keyPlaceholder": "sk-..."
    },
    {
      "id": "kimi",
      "label": "Kimi（月之暗面）",
      "protocol": "openai"
    }
  ]
  
  ```

- [ ] 支持更多国外模型，如Grok

- [ ] 支持快速切换已保存的模型配置

- [x] 重构项目架构

  1）一个文件最多不超过800行，超过就拆分出组件/hook/server

  2）ts/py文件顶部需要注释说明本文件逻辑，方便快速定位

  3）前端架构太丑陋了，全放在`components`里干嘛，安装当下最流行的架构重构下，最起码vue router这些得安装吧，utils、store、hooks、types、views等等分层得清晰

- [ ] 修复已知bug：

  1）【严重】获取的数据存在误差，如真实换手率是11.80%，传递给模型的确实1180%；我们宁愿少传递些数据，也不能把错误数据传递给模型当参考



#### 后端架构

```
backend/
├── api/                    # API 路由层（类似前端 views）
│   ├── health.py           # 健康检查 API
│   ├── stocks.py           # 股票管理 API
│   ├── settings.py         # 设置管理 API
│   ├── alerts.py           # 预警管理 API
│   ├── market.py           # 大盘市场 API
│   ├── ai.py               # AI 分析 API
│   ├── records.py          # 交易记录 API
│   ├── simulation.py       # 实盘模拟 API
│   ├── notes.py            # 笔记管理 API
│   └── data.py             # 数据导入导出 API
│
├── schemas/                # 数据模型定义（类似前端 types）
│   ├── ai.py               # AI 相关模型
│   ├── records.py          # 交易记录模型
│   ├── simulation.py       # 模拟相关模型
│   ├── notes.py            # 笔记相关模型
│   └── data.py             # 数据导入导出模型
│
├── domain/                 # 业务领域层（类似前端 composables/hooks）
│   ├── stock_monitor.py    # 股票监控核心（整合各管理器）
│   ├── stock_manager.py    # 股票列表管理
│   ├── alert_manager.py    # 预警管理
│   ├── records_manager.py  # 交易记录管理
│   ├── simulation_manager.py # 模拟交易管理
│   └── notes_manager.py    # 笔记管理
│
├── services/               # 业务服务层
│   └── ai_service.py       # AI 分析服务
│
├── providers/              # AI 模型提供商（基础设施层）
│   ├── config.py           # 提供商配置和注册表
│   └── protocols.py        # 协议实现（OpenAI/Gemini/Claude/豆包/GLM）
│
├── repositories/           # 数据存储层
│   ├── records_repo.py     # 交易记录存储
│   ├── simulation_repo.py  # 模拟会话存储
│   └── notes_repo.py       # 笔记存储
│
├── core/                   # 核心配置和工具
│   ├── config.py           # 配置管理（数据路径等）
│   ├── stock_data.py       # 股票数据获取器
│   └── index_data.py       # 指数数据获取器
│
├── debug/                   # 调试工具
│
├── requirements.txt        # 依赖
│
├── main.py                 # 应用入口（只做装配）
│
└── *.py                    # 向后兼容文件（重定向到新模块）
```

