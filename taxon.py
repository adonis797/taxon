import os
import time
import threading
from pathlib import Path
from typing import Optional
import typer
from typer import Typer
from models.organizer import DownloadOrganizer
from models.rules import RuleEngine, Rule, RuleType
from utils.config_manager import ConfigManager

app = Typer(help="下载文件夹整理器 - 自动整理下载文件夹中的文件")


@app.command(short_help="整理指定文件夹中的文件", no_args_is_help=True)
def organize(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="要整理的文件夹路径（默认使用配置中的路径）"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="只模拟运行，不实际移动文件"),
    conflict: Optional[str] = typer.Option(
        None,
        "--conflict",
        "-c",
        help="冲突解决策略: rename（重命名，默认）、skip（跳过）、overwrite（覆盖）",
    ),
):
    """整理指定文件夹中的文件，根据扩展名和自定义规则自动分类"""
    config = ConfigManager()
    rule_engine = config.get_rule_engine()

    # 确定要整理的路径
    target_path = path or config.get_download_path()
    if not Path(target_path).exists():
        typer.echo(f"错误：路径不存在: {target_path}", err=True)
        raise typer.Exit(1)

    # 确定冲突解决策略
    conflict_resolution = conflict or config.get_conflict_resolution()

    # 创建整理器并运行
    organizer = DownloadOrganizer(
        path=target_path,
        dry_run=dry_run or config.get_dry_run(),
        rule_engine=rule_engine if rule_engine.rules else None,
        conflict_resolution=conflict_resolution,
    )

    typer.echo(f"开始整理文件夹: {target_path}")
    organizer.organize_files()

    stats = organizer.get_stats()
    typer.echo(f"\n统计信息:")
    typer.echo(f"  移动: {stats['moved']} 个文件")
    typer.echo(f"  跳过: {stats['skipped']} 个文件")
    typer.echo(f"  错误: {stats['errors']} 个文件")


@app.command(short_help="定时运行整理任务")
def schedule(
    interval: int = typer.Option(60, "--interval", "-i", help="运行间隔（分钟）"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="要整理的文件夹路径"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="只模拟运行"),
):
    """定时运行整理任务"""
    if interval < 1:
        typer.echo("错误：运行间隔必须大于等于1分钟", err=True)
        raise typer.Exit(1)
    
    config = ConfigManager()
    rule_engine = config.get_rule_engine()
    target_path = path or config.get_download_path()

    if not Path(target_path).exists():
        typer.echo(f"错误：路径不存在: {target_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"定时整理已启动，每 {interval} 分钟运行一次")
    typer.echo(f"目标文件夹: {target_path}")
    typer.echo("按 Ctrl+C 停止")

    def run_organize():
        organizer = DownloadOrganizer(
            path=target_path,
            dry_run=dry_run,
            rule_engine=rule_engine if rule_engine.rules else None,
            conflict_resolution=config.get_conflict_resolution(),
        )
        organizer.organize_files()

    try:
        while True:
            run_organize()
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        typer.echo("\n定时任务已停止")


@app.command(short_help="管理自定义规则")
def rules(
    action: str = typer.Argument(..., help="操作: list（列出）、add（添加）、remove（删除）、clear（清空）"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="规则名称"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="规则类型: keyword（关键词）、regex（正则）、extension（扩展名）"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="匹配模式"),
    folder: Optional[str] = typer.Option(None, "--folder", "-f", help="目标文件夹"),
    priority: Optional[int] = typer.Option(None, "--priority", help="优先级（数字越大优先级越高）"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="是否区分大小写"),
):
    """管理自定义分类规则"""
    config = ConfigManager()
    rule_engine = config.get_rule_engine()

    if action == "list":
        if not rule_engine.rules:
            typer.echo("没有自定义规则")
            return

        typer.echo("\n自定义规则列表:")
        typer.echo("-" * 80)
        for rule in rule_engine.rules:
            typer.echo(f"名称: {rule.name}")
            typer.echo(f"  类型: {rule.rule_type.value}")
            typer.echo(f"  模式: {rule.pattern}")
            typer.echo(f"  目标文件夹: {rule.target_folder}")
            typer.echo(f"  优先级: {rule.priority}")
            typer.echo(f"  区分大小写: {rule.case_sensitive}")
            typer.echo()

    elif action == "add":
        if not all([name, type, pattern, folder]):
            typer.echo("错误：添加规则需要提供 --name, --type, --pattern, --folder 参数", err=True)
            raise typer.Exit(1)

        try:
            rule_type = RuleType(type.lower())
        except ValueError:
            typer.echo(f"错误：无效的规则类型: {type}。可选值: keyword, regex, extension", err=True)
            raise typer.Exit(1)

        rule = Rule(
            name=name,
            rule_type=rule_type,
            pattern=pattern,
            target_folder=folder,
            priority=priority or 0,
            case_sensitive=case_sensitive,
        )
        rule_engine.add_rule(rule)
        config.save_rule_engine(rule_engine)
        typer.echo(f"规则 '{name}' 已添加")

    elif action == "remove":
        if not name:
            typer.echo("错误：删除规则需要提供 --name 参数", err=True)
            raise typer.Exit(1)

        if rule_engine.remove_rule(name):
            config.save_rule_engine(rule_engine)
            typer.echo(f"规则 '{name}' 已删除")
        else:
            typer.echo(f"错误：未找到规则 '{name}'", err=True)
            raise typer.Exit(1)

    elif action == "clear":
        rule_engine.rules.clear()
        config.save_rule_engine(rule_engine)
        typer.echo("所有规则已清空")

    else:
        typer.echo(f"错误：未知操作 '{action}'", err=True)
        typer.echo("可用操作: list, add, remove, clear")
        raise typer.Exit(1)


@app.command(name="config", short_help="配置管理")
def config_cmd(
    action: str = typer.Argument(..., help="操作: show（显示）、set-path（设置下载路径）、set-conflict（设置冲突策略）"),
    value: Optional[str] = typer.Option(None, help="配置值"),
):
    """管理配置"""
    config = ConfigManager()

    if action == "show":
        typer.echo("\n当前配置:")
        typer.echo(f"  下载文件夹: {config.get_download_path()}")
        typer.echo(f"  冲突解决策略: {config.get_conflict_resolution()}")
        typer.echo(f"  干运行模式: {config.get_dry_run()}")
        typer.echo(f"  配置文件路径: {config.config_path}")

    elif action == "set-path":
        if not value:
            typer.echo("错误：需要提供路径", err=True)
            raise typer.Exit(1)
        if not Path(value).exists():
            typer.echo(f"警告：路径不存在: {value}", err=True)
        config.set_download_path(value)
        typer.echo(f"下载文件夹已设置为: {value}")

    elif action == "set-conflict":
        if not value:
            typer.echo("错误：需要提供策略（rename/skip/overwrite）", err=True)
            raise typer.Exit(1)
        try:
            config.set_conflict_resolution(value)
            typer.echo(f"冲突解决策略已设置为: {value}")
        except ValueError as e:
            typer.echo(f"错误: {e}", err=True)
            raise typer.Exit(1)

    else:
        typer.echo(f"错误：未知操作 '{action}'", err=True)
        typer.echo("可用操作: show, set-path, set-conflict")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
