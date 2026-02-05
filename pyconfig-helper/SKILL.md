---
description: Python项目配置管理最佳实践（K8s + GitLab CI/CD）
---

# Python 项目配置管理最佳实践

## 背景与目标

- **技术栈**：Python 项目 + K8s 部署 + GitLab CI/CD
- **环境**：develop / staging / production
- **目标**：安全、可维护、环境隔离、本地开发友好

---

## 配置分类

| 类型 | 描述 | 本地存放 | K8s存放 | 示例 |
|------|------|----------|---------|------|
| **敏感配置** | 密码、密钥、凭证 | `.env`（不入库） | GitLab CI/CD Variables → `sed`替换 | `DB_PASSWORD`, `AWS_SECRET_KEY` |
| **环境配置** | 因环境而异的非敏感配置 | `config/{env}.yaml` | `overlays/{env}/configmap.yaml` | `DB_HOST`, `API_URL`, `LOG_LEVEL` |
| **应用常量** | 所有环境共享 | `config/base.yaml` 或代码默认值 | 包含在 `overlays/{env}/configmap.yaml` 中 | `MAX_WORKERS`, `BATCH_SIZE` |

---

## 项目文件结构

```
project-root/
├── app/
│   ├── settings.py               # 配置加载模块（Pydantic Settings）
│   └── ...
│
├── config/                        # 本地配置文件（可自定义环境名）
│   ├── base.yaml                  # 基础配置（共享常量，严格要求需要包含所有的key，敏感配置value为空）
│   └── {env}.yaml                 # 环境配置（如 dev.yaml, test.yaml, debug.yaml 等，用于覆盖base的配置）
│
├── .env.example                   # 敏感变量模板（入库）
├── .env                           # 本地敏感配置（不入库，本地开发使用，线上请使用环境变量）
│
└── deploy/kustomize/              # K8s部署配置
    ├── base/
    │   ├── kustomization.yaml
    │   └── cronjob.yaml         
    │
    └── overlays/
        ├── develop/
        │   ├── kustomization.yaml
        │   ├── cronjob.yaml
        │   └── configmap.yaml     # 来源base.yml，环境配置 + 敏感占位符
        ├── staging/
        │   └── configmap.yaml
        └── production/
            └── configmap.yaml
```

---

## 配置文件格式（嵌套 YAML）

### 本地配置示例

```yaml
# config/config.yaml
# 优先级：环境变量 > YAML配置 > 代码默认值

# ===== 数据库配置 =====
database:
  host: localhost
  port: 3306
  user: root
  password: ""  # 敏感，从 .env 读取

# ===== 外部服务 =====
api:
  url: http://localhost:8080/api
  timeout: 5000

# ===== 应用配置 =====
app:
  max_workers: 20
  batch_size: 1000
  max_retry: 3
  log_level: INFO
```

> [!NOTE]
> - **本地**：`config/base.yaml` 存放完整配置模板，`config/{env}.yaml` 用于覆盖形成不同环境
> - **K8s**：`overlays/{env}/configmap.yaml` 存放完整配置（来源于 base.yaml，包含敏感占位符）
> 使用嵌套结构可读性更好，本地和 K8s 配置格式完全一致。
---

## 敏感信息管理

### 核心原则

> [!CAUTION]
> 敏感信息（密码、密钥）**永不直接入库**。CI/CD 只替换 `deploy/` 下的配置文件，不替换代码文件。

### 设计思路

```
代码                                K8s部署文件                      运行时
-----                               ----------                       ------
从环境变量读取     ←     ConfigMap挂载为环境变量     ←     CI/CD替换占位符
settings.db_password        configmap.yaml                   GitLab Variables
```

### GitLab CI/CD 变量配置

在 GitLab 项目的 **Settings → CI/CD → Variables** 中配置：

| 变量名 | 环境 | 说明 |
|--------|------|------|
| `MYSQL_PASSWORD_DEV` | develop | 开发环境数据库密码 |
| `MYSQL_PASSWORD_STAGING` | staging | 预发布环境数据库密码 |
| `MYSQL_PASSWORD_PRODUCTION` | production | 生产环境数据库密码 |

> [!TIP]
> 生产环境变量建议设置为 **Protected** 和 **Masked**。

### ConfigMap 配置（含敏感占位符）

```yaml
# deploy/kustomize/overlays/develop/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.yaml: |
    # ===== 数据库配置 =====
    database:
      host: mysql-svc.database-dev.svc.cluster.local
      port: 3306
      user: root
      password: MYSQL_PASSWORD_DEV  # CI 时替换

    # ===== 外部服务 =====
    api:
      url: http://api-svc.app-dev.svc.cluster.local/api/v1
      timeout: 5000

    # ===== 应用配置 =====
    app:
      max_workers: 20
      batch_size: 1000
      max_retry: 3
      log_level: DEBUG
```

### CI/CD 替换敏感占位符

```yaml
# .gitlab-ci.yml
deploy:develop:
  script:
    # 替换 ConfigMap 中的敏感占位符
    - sed -i "s|MYSQL_PASSWORD_DEV|${MYSQL_PASSWORD_DEV}|g" deploy/kustomize/overlays/develop/configmap.yaml
    - sed -i "s|AWS_ACCESS_KEY_ID|${AWS_ACCESS_KEY_ID}|g" deploy/kustomize/overlays/develop/configmap.yaml
    - sed -i "s|AWS_SECRET_ACCESS_KEY|${AWS_SECRET_ACCESS_KEY}|g" deploy/kustomize/overlays/develop/configmap.yaml
    # 替换镜像标签等其他占位符
    - sed -i "s|IMAGE_TAG|${IMAGE}:${CI_APP_TAG}|g" deploy/kustomize/overlays/develop/cronjob.yaml
    # 应用配置
    - kubectl apply -k deploy/kustomize/overlays/develop/

```

### 工作负载挂载 ConfigMap 为文件

```yaml
# cronjob.yaml 或 deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: app
        env:
          - name: CONFIG_PATH
            value: "/app/config/config.yaml"
        volumeMounts:
          - name: config-volume
            mountPath: /app/config/config.yaml
            subPath: config.yaml
            readOnly: true
      volumes:
        - name: config-volume
          configMap:
            name: app-config
            items:
              - key: config.yaml
                path: config.yaml
```

> [!NOTE]
> ConfigMap 作为文件挂载后，修改 ConfigMap 内容时，文件会自动更新（热更新）。



---

## 配置加载实现（Pydantic Settings）

完整的配置加载模块示例：

📄 **[settings.py](reference/settings.py)**

核心功能：
- 使用 Pydantic Settings 自动从环境变量加载配置
- 支持 `.env` 文件加载（本地开发）
- 支持 YAML 配置文件加载（可选）
- 单例模式（`@lru_cache`）确保全局一致

### 使用方式

```python
from settings import settings

# 访问嵌套配置
print(settings.database.host)
print(settings.app.max_workers)
print(settings.logging.level)
```

---

## 配置加载优先级

```
环境变量（运行时最高优先级）
    ↓
.env 文件（敏感配置）
    ↓
YAML 配置文件（CONFIG_PATH 指定）
    ↓
代码默认值
```

在 K8s 环境中，ConfigMap 作为文件挂载到 `/app/config/config.yaml`。

---

## 本地开发

### 环境切换

通过 `.env` 中的 `CONFIG_PATH` 指定配置文件路径，切换时修改即可。

### .env 示例

```bash
# .env.example（入库） / .env（不入库）
CONFIG_PATH=config/config.yaml
DATABASE_PASSWORD=          # 本地填写实际值
```

> [!NOTE]
> 本地开发时，非敏感配置从 YAML 读取，敏感配置从 `.env` 读取并覆盖 YAML 值。

---

## .gitignore 配置

```gitignore
# 敏感配置
.env

# 保留模板
!.env.example
```

---

## 配置命名规范

| 位置 | 规范 | 示例 |
|------|------|------|
| YAML 配置 | 小写 + 下划线 + 嵌套 | `database.host`, `app.max_workers` |
| 环境变量（敏感配置） | 大写 + 下划线 | `DATABASE_PASSWORD` |
| 敏感占位符 | 大写 + 环境后缀 | `MYSQL_PASSWORD_DEV` |

---

## 检查清单

- [ ] 敏感信息使用占位符，存放在 GitLab CI/CD Variables
- [ ] 本地有 `config/config.yaml` 或 `config/base.yaml` + `config/{env}.yaml`
- [ ] K8s 每个 overlay 有 `configmap.yaml`（完整 YAML 作为文件）
- [ ] Deployment/CronJob 正确挂载 ConfigMap 为文件
- [ ] CI/CD 正确执行 `sed` 替换敏感值
- [ ] `.env` 已添加到 `.gitignore`
- [ ] 提供 `.env.example` 模板

---

## 参考资料

- [12-Factor App: Config](https://12factor.net/config)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)