#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Processing Module for GLM-5.1 API
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
except ImportError:
    Console = None


@dataclass
class BatchJob:
    """Batch job configuration"""
    job_id: str
    input_file: Path
    output_file: Path
    system_message: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "input_file": str(self.input_file),
            "output_file": str(self.output_file),
            "system_message": self.system_message,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


@dataclass
class BatchResult:
    """Batch processing result"""
    job_id: str
    total: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    duration: float
    start_time: float
    end_time: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "success_rate": f"{(self.successful / self.total * 100):.2f}%" if self.total > 0 else "0%",
            "errors": self.errors
        }


class BatchProcessor:
    """
    Batch processor for GLM-5.1 API

    Features:
    - Multi-threaded processing
    - Progress tracking
    - Error handling
    - Result aggregation
    - Checkpoint support
    """

    def __init__(
        self,
        client,
        max_workers: int = 5,
        checkpoint_interval: int = 10,
        checkpoint_file: Optional[Path] = None
    ):
        """
        Initialize batch processor

        Args:
            client: GLMAPIClient instance
            max_workers: Maximum concurrent workers
            checkpoint_interval: Save checkpoint every N items
            checkpoint_file: Checkpoint file path
        """
        self.client = client
        self.max_workers = max_workers
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_file = checkpoint_file

        self.console = Console() if Console else None
        self.lock = threading.Lock()

    def _load_input_file(self, input_file: Path) -> List[Dict[str, Any]]:
        """Load input from file"""
        if input_file.suffix == '.json':
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'prompts' in data:
                    return data['prompts']
                else:
                    return [data]
        elif input_file.suffix == '.txt':
            with open(input_file, 'r', encoding='utf-8') as f:
                return [{"prompt": line.strip()} for line in f if line.strip()]
        else:
            raise ValueError(f"Unsupported file format: {input_file.suffix}")

    def _save_results(self, output_file: Path, results: List[Dict[str, Any]]):
        """Save results to file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix == '.json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, result in enumerate(results):
                    f.write(f"--- Result {i + 1} ---\n")
                    f.write(result.get('response', result.get('error', '')))
                    f.write("\n\n")

    def process_batch(
        self,
        input_file: Path,
        output_file: Path,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        show_progress: bool = True
    ) -> BatchResult:
        """
        Process batch of prompts

        Args:
            input_file: Input file path (JSON or TXT)
            output_file: Output file path
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            show_progress: Show progress bar

        Returns:
            BatchResult object
        """
        start_time = time.time()

        # Load input data
        try:
            items = self._load_input_file(input_file)
        except Exception as e:
            return BatchResult(
                job_id="",
                total=0,
                successful=0,
                failed=0,
                results=[],
                errors=[{"error": str(e)}],
                duration=0,
                start_time=start_time,
                end_time=time.time()
            )

        total = len(items)
        results = []
        errors = []
        successful = 0
        failed = 0

        # Process items
        if show_progress and self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Processing {total} items...",
                    total=total
                )

                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {
                        executor.submit(
                            self._process_item,
                            item,
                            system_message,
                            temperature,
                            max_tokens
                        ): i
                        for i, item in enumerate(items)
                    }

                    for future in as_completed(futures):
                        idx = futures[future]
                        try:
                            result = future.result()
                            results.append(result)

                            if result.get('error'):
                                failed += 1
                                errors.append({
                                    "index": idx,
                                    "prompt": items[idx].get('prompt', '')[:100],
                                    "error": result.get('error')
                                })
                            else:
                                successful += 1

                        except Exception as e:
                            failed += 1
                            errors.append({
                                "index": idx,
                                "prompt": items[idx].get('prompt', '')[:100],
                                "error": str(e)
                            })

                        progress.update(task, advance=1)

                        # Checkpoint
                        if (idx + 1) % self.checkpoint_interval == 0:
                            self._save_checkpoint(results)
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(
                        self._process_item,
                        item,
                        system_message,
                        temperature,
                        max_tokens
                    ): i
                    for i, item in enumerate(items)
                }

                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        result = future.result()
                        results.append(result)

                        if result.get('error'):
                            failed += 1
                        else:
                            successful += 1

                    except Exception as e:
                        failed += 1
                        errors.append({
                            "index": idx,
                            "error": str(e)
                        })

        # Save results
        self._save_results(output_file, results)

        end_time = time.time()

        return BatchResult(
            job_id=str(input_file.stem),
            total=total,
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
            duration=end_time - start_time,
            start_time=start_time,
            end_time=end_time
        )

    def _process_item(
        self,
        item: Dict[str, Any],
        system_message: Optional[str],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Process single item"""
        prompt = item.get('prompt', item.get('content', ''))
        custom_system = item.get('system', system_message)

        try:
            response = self.client.simple_chat(
                prompt=prompt,
                system_message=custom_system,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "prompt": prompt,
                "response": response,
                "success": True
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "error": str(e),
                "success": False
            }

    def _save_checkpoint(self, results: List[Dict[str, Any]]):
        """Save checkpoint file"""
        if self.checkpoint_file:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    def print_summary(self, result: BatchResult):
        """Print batch processing summary"""
        if not self.console:
            return

        table = Table(title="Batch Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Items", str(result.total))
        table.add_row("Successful", str(result.successful))
        table.add_row("Failed", str(result.failed))
        table.add_row("Success Rate", result.to_dict()["success_rate"])
        table.add_row("Duration", f"{result.duration:.2f}s")
        table.add_row("Avg Time/Item", f"{result.duration / result.total:.2f}s" if result.total > 0 else "N/A")

        self.console.print(table)

        if result.errors:
            self.console.print(f"\n[yellow]Errors encountered: {len(result.errors)}[/yellow]")
            for error in result.errors[:5]:
                self.console.print(f"  - {error.get('prompt', 'N/A')[:50]}... : {error.get('error', 'Unknown')}")
