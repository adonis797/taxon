import re
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class RuleType(Enum):
    """规则类型枚举"""
    KEYWORD = "keyword"  # 关键词匹配
    REGEX = "regex"  # 正则表达式匹配
    EXTENSION = "extension"  # 扩展名匹配


@dataclass
class Rule:
    """文件分类规则"""
    name: str  # 规则名称
    rule_type: RuleType  # 规则类型
    pattern: str  # 匹配模式（关键词、正则表达式或扩展名）
    target_folder: str  # 目标文件夹
    priority: int = 0  # 优先级（数字越大优先级越高）
    case_sensitive: bool = False  # 是否区分大小写

    def matches(self, filename: str) -> bool:
        """检查文件名是否匹配此规则"""
        if not self.case_sensitive:
            filename = filename.lower()
            pattern = self.pattern.lower()
        else:
            pattern = self.pattern

        if self.rule_type == RuleType.KEYWORD:
            return pattern in filename
        elif self.rule_type == RuleType.REGEX:
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, filename, flags))
            except re.error:
                return False
        elif self.rule_type == RuleType.EXTENSION:
            return filename.endswith(pattern)
        return False


class RuleEngine:
    """规则引擎：管理和应用文件分类规则"""

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules or []
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_name: str) -> bool:
        """移除规则"""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < original_count

    def find_matching_rule(self, filename: str) -> Optional[Rule]:
        """查找匹配文件名的规则"""
        for rule in self.rules:
            if rule.matches(filename):
                return rule
        return None

    def get_target_folder(self, filename: str, default_folder: str = "others") -> str:
        """获取文件的目标文件夹"""
        rule = self.find_matching_rule(filename)
        return rule.target_folder if rule else default_folder

    def to_dict(self) -> List[Dict]:
        """转换为字典列表（用于序列化）"""
        return [
            {
                "name": rule.name,
                "rule_type": rule.rule_type.value,
                "pattern": rule.pattern,
                "target_folder": rule.target_folder,
                "priority": rule.priority,
                "case_sensitive": rule.case_sensitive,
            }
            for rule in self.rules
        ]

    @classmethod
    def from_dict(cls, rules_data: List[Dict]) -> "RuleEngine":
        """从字典列表创建规则引擎（用于反序列化）"""
        rules = []
        for rule_data in rules_data:
            rule = Rule(
                name=rule_data["name"],
                rule_type=RuleType(rule_data["rule_type"]),
                pattern=rule_data["pattern"],
                target_folder=rule_data["target_folder"],
                priority=rule_data.get("priority", 0),
                case_sensitive=rule_data.get("case_sensitive", False),
            )
            rules.append(rule)
        return cls(rules)

