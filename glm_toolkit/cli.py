#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Interface for GLM-5.1 API Toolkit
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
except ImportError:
    Console = None
    Panel = None
    Markdown = None
    Syntax = None

from . import __version__
from .sdk import GLMAPIClient, GLMMessage
from .config import ConfigManager
from .cache import CacheManager
from .rate_limiter import RateLimiter
from .batch import BatchProcessor


console = Console() if Console else None


def get_client(
    api_key: Optional[str] = None,
    config_file: Optional[Path] = None,
    use_cache: bool = True,
    use_rate_limit: bool = True
) -> GLMAPIClient:
    """
    Initialize GLM API client with configuration

    Args:
        api_key: Optional API key override
        config_file: Optional config file path
        use_cache: Enable caching
        use_rate_limit: Enable rate limiting

    Returns:
        Configured GLMAPIClient instance
    """
    # Load configuration
    config_manager = ConfigManager(config_file) if config_file else ConfigManager()
    config = config_manager.get_config()

    # Get API key
    final_api_key = api_key or config.api_key
    if not final_api_key:
        raise ValueError(
            "API key not found. Set GLM_API_KEY environment variable or run:\n"
            "glm-toolkit config --set-api-key YOUR_API_KEY"
        )

    # Initialize optional components
    cache_manager = None
    rate_limiter = None

    if use_cache and config.cache_enabled:
        try:
            cache_manager = CacheManager(cache_dir=config.cache_dir)
        except Exception as e:
            if console:
                console.print(f"[yellow]Warning: Cache initialization failed: {e}[/yellow]")

    if use_rate_limit and config.rate_limit_enabled:
        rate_limiter = RateLimiter(
            requests=config.rate_limit_requests,
            period=config.rate_limit_period
        )

    return GLMAPIClient(
        api_key=final_api_key,
        api_url=config.api_url,
        model=config.model,
        timeout=config.timeout,
        max_retries=config.max_retries,
        cache_manager=cache_manager,
        rate_limiter=rate_limiter
    )


@click.group()
@click.version_option(version=__version__)
def main():
    """GLM-5.1 API Toolkit - Comprehensive API management tool"""
    pass


@main.command()
@click.argument('prompt')
@click.option('--system', '-s', help='System message')
@click.option('--temperature', '-t', default=0.7, help='Sampling temperature (0.0-2.0)')
@click.option('--max-tokens', '-m', default=None, type=int, help='Maximum tokens in response')
@click.option('--api-key', '-k', help='API key (or set GLM_API_KEY env var)')
@click.option('--no-cache', is_flag=True, help='Disable response caching')
@click.option('--no-rate-limit', is_flag=True, help='Disable rate limiting')
def chat(prompt: str, system: Optional[str], temperature: float, max_tokens: Optional[int],
         api_key: Optional[str], no_cache: bool, no_rate_limit: bool):
    """Send a chat request to GLM-5.1"""
    try:
        client = get_client(api_key, use_cache=not no_cache, use_rate_limit=not no_rate_limit)

        with client:
            response = client.simple_chat(
                prompt=prompt,
                system_message=system,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if console:
                console.print(Panel(
                    response,
                    title="GLM-5.1 Response",
                    border_style="green"
                ))
            else:
                print(response)

    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@main.command()
@click.option('--input', '-i', 'input_file', required=True, type=click.Path(exists=True), help='Input file (JSON or TXT)')
@click.option('--output', '-o', 'output_file', required=True, type=click.Path(), help='Output file path')
@click.option('--system', '-s', help='System message')
@click.option('--temperature', '-t', default=0.7, help='Sampling temperature')
@click.option('--max-tokens', '-m', type=int, help='Maximum tokens per response')
@click.option('--workers', '-w', default=5, help='Number of concurrent workers')
@click.option('--api-key', '-k', help='API key')
def batch(input_file: Path, output_file: Path, system: Optional[str], temperature: float,
          max_tokens: Optional[int], workers: int, api_key: Optional[str]):
    """Process batch of prompts from file"""
    try:
        client = get_client(api_key)
        processor = BatchProcessor(client, max_workers=workers)

        with client:
            result = processor.process_batch(
                input_file=input_file,
                output_file=output_file,
                system_message=system,
                temperature=temperature,
                max_tokens=max_tokens
            )

            processor.print_summary(result)

            if console:
                console.print(f"\n[green]Results saved to: {output_file}[/green]")

    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@main.command()
@click.option('--set-api-key', help='Set API key')
@click.option('--set-model', help='Set default model')
@click.option('--set-api-url', help='Set API URL')
@click.option('--show', is_flag=True, help='Show current configuration')
def config(set_api_key: Optional[str], set_model: Optional[str], set_api_url: Optional[str], show: bool):
    """Manage configuration"""
    manager = ConfigManager()

    if show:
        config = manager.get_config()
        if console:
            table = console.table(title="Current Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="magenta")

            for key, value in config.to_dict().items():
                if key != "api_key" or value:
                    display_value = "***" + value[-4:] if key == "api_key" and value else value
                    table.add_row(key, str(display_value))

            console.print(table)
        return

    if set_api_key:
        manager.update_config(api_key=set_api_key)
        manager.save_config()
        if console:
            console.print("[green]API key updated successfully[/green]")

    if set_model:
        manager.update_config(model=set_model)
        manager.save_config()
        if console:
            console.print(f"[green]Default model set to: {set_model}[/green]")

    if set_api_url:
        manager.update_config(api_url=set_api_url)
        manager.save_config()
        if console:
            console.print(f"[green]API URL set to: {set_api_url}[/green]")


@main.command()
@click.option('--clear', is_flag=True, help='Clear all cache')
def cache(clear: bool):
    """Manage response cache"""
    manager = ConfigManager()
    config = manager.get_config()

    try:
        cache = CacheManager(cache_dir=config.cache_dir)

        if clear:
            cache.clear()
            if console:
                console.print("[green]Cache cleared successfully[/green]")
        else:
            stats = cache.get_stats()
            if console:
                table = console.table(title="Cache Statistics")
                for key, value in stats.items():
                    table.add_row(key, str(value))
                console.print(table)

        cache.close()

    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}", file=sys.stderr)


@main.command()
def stats():
    """Show usage statistics"""
    try:
        client = get_client()
        usage = client.get_usage_stats()

        if console:
            table = console.table(title="API Statistics")
            for key, value in usage.items():
                table.add_row(key, str(value))
            console.print(table)

        # Cache stats
        manager = ConfigManager()
        config = manager.get_config()

        if config.cache_enabled:
            try:
                cache = CacheManager(cache_dir=config.cache_dir)
                cache_stats = cache.get_stats()
                if console:
                    console.print("\n[cyan]Cache Statistics:[/cyan]")
                    for key, value in cache_stats.items():
                        console.print(f"  {key}: {value}")
                cache.close()
            except:
                pass

        client.close()

    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}", file=sys.stderr)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output markdown file')
def help_docs(input_file: Path, output: Optional[Path]):
    """Generate help documentation from INPUT file"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"# Documentation\n\n{content}")
            if console:
                console.print(f"[green]Documentation saved to: {output}[/green]")
        else:
            if console:
                console.print(content)
            else:
                print(content)

    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
