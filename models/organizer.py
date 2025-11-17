import os
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from utils.file_utils import get_file_category, setup_logger
from models.rules import RuleEngine


class DownloadOrganizer:
    """下载文件夹整理器"""

    def __init__(
        self,
        path: str,
        dry_run: bool = False,
        rule_engine: Optional[RuleEngine] = None,
        conflict_resolution: str = "rename",
    ):
        """
        初始化整理器

        Args:
            path: 要整理的文件夹路径
            dry_run: 是否只模拟运行（不实际移动文件）
            rule_engine: 自定义规则引擎
            conflict_resolution: 冲突解决策略 (rename, skip, overwrite)
        """
        self.path = Path(path)
        if not self.path.exists():
            raise ValueError(f"路径不存在: {path}")
        if not self.path.is_dir():
            raise ValueError(f"路径不是文件夹: {path}")

        self.dry_run = dry_run
        self.rule_engine = rule_engine
        self.conflict_resolution = conflict_resolution
        self.logger = setup_logger(self.__class__.__name__)

        # 统计信息
        self.stats = {
            "moved": 0,
            "skipped": 0,
            "errors": 0,
        }

    def get_files(self) -> List[Path]:
        """获取文件夹中的所有文件（不包括子文件夹中的文件）"""
        return [
            f for f in self.path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]

    def organize_files(self):
        """整理文件"""
        files = self.get_files()
        self.logger.info(f"找到 {len(files)} 个文件需要整理")

        for file_path in files:
            try:
                self._organize_file(file_path)
            except Exception as e:
                self.logger.error(f"处理文件 {file_path.name} 时出错: {e}")
                self.stats["errors"] += 1

        self.logger.info(
            f"整理完成: 移动 {self.stats['moved']} 个文件, "
            f"跳过 {self.stats['skipped']} 个文件, "
            f"错误 {self.stats['errors']} 个文件"
        )

    def _organize_file(self, file_path: Path):
        """整理单个文件"""
        filename = file_path.name

        # 优先使用自定义规则
        if self.rule_engine:
            category = self.rule_engine.get_target_folder(filename)
        else:
            # 使用默认的扩展名分类
            extension = file_path.suffix
            category = get_file_category(extension)

        target_dir = self.path / category
        target_path = target_dir / filename

        # 处理文件名冲突
        if target_path.exists() and target_path != file_path:
            target_path = self._resolve_conflict(file_path, target_dir, filename)
            if target_path is None:
                self.stats["skipped"] += 1
                return

        # 移动文件
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))
            self.logger.info(f"移动: {file_path.name} -> {category}/{target_path.name}")
        else:
            self.logger.info(f"[模拟] 移动: {file_path.name} -> {category}/{target_path.name}")

        self.stats["moved"] += 1

    def _resolve_conflict(self, file_path: Path, target_dir: Path, filename: str) -> Optional[Path]:
        """解决文件名冲突"""
        if self.conflict_resolution == "skip":
            self.logger.warning(f"跳过文件（已存在）: {filename}")
            return None
        elif self.conflict_resolution == "overwrite":
            self.logger.warning(f"覆盖文件: {filename}")
            return target_dir / filename
        else:  # rename
            new_name = self._get_unique_file_name(target_dir, filename)
            return target_dir / new_name

    def _get_unique_file_name(self, target_dir: Path, filename: str) -> str:
        """生成唯一的文件名（添加数字后缀）"""
        base_name, extension = os.path.splitext(filename)
        count = 1

        while True:
            new_name = f"{base_name}_{count}{extension}"
            new_path = target_dir / new_name
            if not new_path.exists():
                return new_name
            count += 1

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()