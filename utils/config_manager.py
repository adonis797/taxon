import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from models.rules import RuleEngine, Rule, RuleType


class ConfigManager:
    """配置管理器：处理配置文件的读写"""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # 默认配置文件路径：用户主目录下的 .taxon_config.json
            self.config_path = Path.home() / ".taxon_config.json"
        else:
            self.config_path = Path(config_path)

        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告：配置文件加载失败，使用默认配置: {e}")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "default_download_path": str(Path.home() / "Downloads"),
            "rules": [],
            "conflict_resolution": "rename",  # rename, skip, overwrite
            "dry_run": False,
        }

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"错误：配置文件保存失败: {e}")

    def get_download_path(self) -> str:
        """获取下载文件夹路径"""
        return self.config.get("default_download_path", str(Path.home() / "Downloads"))

    def set_download_path(self, path: str):
        """设置下载文件夹路径"""
        self.config["default_download_path"] = path
        self.save_config()

    def get_rule_engine(self) -> RuleEngine:
        """获取规则引擎"""
        rules_data = self.config.get("rules", [])
        return RuleEngine.from_dict(rules_data)

    def save_rule_engine(self, rule_engine: RuleEngine):
        """保存规则引擎"""
        self.config["rules"] = rule_engine.to_dict()
        self.save_config()

    def get_conflict_resolution(self) -> str:
        """获取冲突解决策略"""
        return self.config.get("conflict_resolution", "rename")

    def set_conflict_resolution(self, strategy: str):
        """设置冲突解决策略"""
        if strategy not in ["rename", "skip", "overwrite"]:
            raise ValueError(f"无效的冲突解决策略: {strategy}")
        self.config["conflict_resolution"] = strategy
        self.save_config()

    def get_dry_run(self) -> bool:
        """获取是否启用干运行模式"""
        return self.config.get("dry_run", False)

    def set_dry_run(self, dry_run: bool):
        """设置干运行模式"""
        self.config["dry_run"] = dry_run
        self.save_config()

