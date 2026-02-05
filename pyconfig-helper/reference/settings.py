"""
配置管理模块

支持嵌套 YAML 配置文件，与 K8s ConfigMap 挂载文件格式一致。

配置来源：
- 非敏感配置：YAML 配置文件（CONFIG_BASE_PATH + CONFIG_ENV_PATH）
- 敏感配置：.env 文件或环境变量

优先级（从高到低）：
1. 环境变量（运行时最高优先级）
2. .env 文件
3. CONFIG_ENV_PATH 指定的 YAML（环境配置，覆盖基础）
4. CONFIG_BASE_PATH 指定的 YAML（基础配置）
5. 代码默认值

使用方式：
    from settings import settings
    print(settings.database.host)
    print(settings.app.max_workers)
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# =============================================================================
# .env 文件加载
# =============================================================================

def load_dotenv(env_file: str = ".env") -> None:
    """加载 .env 文件到环境变量"""
    env_path = Path(env_file)
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

# 优先加载 .env
load_dotenv()


# =============================================================================
# YAML 配置加载
# =============================================================================

def load_yaml_file(file_path: Optional[str]) -> Dict[str, Any]:
    """
    加载单个 YAML 文件
    
    Args:
        file_path: 配置文件路径，为空或不存在则返回空字典
    
    Returns:
        配置字典（嵌套结构）
    """
    if not file_path:
        return {}
    
    path = Path(file_path)
    if not path.exists():
        return {}
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return config if config else {}


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    深度合并两个字典，override 覆盖 base
    
    Args:
        base: 基础配置
        override: 覆盖配置
    
    Returns:
        合并后的配置
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_merged_config() -> Dict[str, Any]:
    """
    加载并合并 base + env 配置
    
    从 CONFIG_BASE_PATH 和 CONFIG_ENV_PATH 环境变量获取路径，
    加载两个文件并深度合并，env 配置覆盖 base 配置。
    """
    base_path = os.getenv("CONFIG_BASE_PATH", "")
    env_path = os.getenv("CONFIG_ENV_PATH", "")
    
    # 加载基础配置
    base_config = load_yaml_file(base_path)
    
    # 加载环境配置
    env_config = load_yaml_file(env_path)
    
    # 深度合并：环境配置覆盖基础配置
    return deep_merge(base_config, env_config)


# =============================================================================
# 嵌套配置模型
# =============================================================================

class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=3306)
    user: str = Field(default="root")
    password: str = Field(default="")


class ApiConfig(BaseModel):
    """API 配置"""
    url: str = Field(default="http://localhost:8080/api")
    timeout: int = Field(default=5000)


class AppConfig(BaseModel):
    """应用配置"""
    max_workers: int = Field(default=20)
    batch_size: int = Field(default=1000)
    max_retry: int = Field(default=3)
    log_level: str = Field(default="INFO")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO")
    show_progress: bool = Field(default=True)


# =============================================================================
# 主配置类
# =============================================================================

class Settings(BaseSettings):
    """
    应用配置类
    
    配置优先级：
        环境变量 > .env > CONFIG_ENV_PATH > CONFIG_BASE_PATH > 默认值
    """
    
    # 配置文件路径
    config_base_path: str = Field(default="", description="基础配置文件路径")
    config_env_path: str = Field(default="", description="环境配置文件路径")
    
    # 嵌套配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **data):
        # 加载并合并 YAML 配置
        yaml_config = load_merged_config()
        
        # 从 YAML 加载嵌套配置
        if yaml_config:
            if "database" in yaml_config and "database" not in data:
                data["database"] = yaml_config["database"]
            if "api" in yaml_config and "api" not in data:
                data["api"] = yaml_config["api"]
            if "app" in yaml_config and "app" not in data:
                data["app"] = yaml_config["app"]
            if "logging" in yaml_config and "logging" not in data:
                data["logging"] = yaml_config["logging"]
        
        # 环境变量覆盖（敏感配置）
        self._apply_env_overrides(data)
        
        super().__init__(**data)
    
    def _apply_env_overrides(self, data: Dict[str, Any]) -> None:
        """应用环境变量覆盖（主要用于敏感配置）"""
        # 数据库密码
        if os.getenv("DATABASE_PASSWORD"):
            if "database" not in data:
                data["database"] = {}
            if isinstance(data["database"], dict):
                data["database"]["password"] = os.getenv("DATABASE_PASSWORD")
    
    @property
    def db_url(self) -> str:
        """返回数据库连接 URL"""
        return (
            f"mysql+pymysql://{self.database.user}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}"
        )


# =============================================================================
# 单例获取函数
# =============================================================================

@lru_cache
def get_settings() -> Settings:
    """获取配置单例（带缓存）"""
    return Settings()


# 便捷访问
settings = get_settings()


# =============================================================================
# 使用示例
# =============================================================================

if __name__ == "__main__":
    print(f"基础配置: {settings.config_base_path}")
    print(f"环境配置: {settings.config_env_path}")
    print(f"数据库: {settings.database.host}:{settings.database.port}")
    print(f"API: {settings.api.url}")
    print(f"日志级别: {settings.logging.level}")
    print(f"最大线程数: {settings.app.max_workers}")
