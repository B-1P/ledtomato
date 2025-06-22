"""Display and UI components for LED Tomato CLI"""

import time
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich import box
import colorama

# Initialize colorama for Windows color support
colorama.init()


class Display:
    """Display manager for LED Tomato CLI"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        
        # ASCII art tomato
        self.tomato_art = """
     🍅 LED Tomato 🍅
    ╭─────────────────╮
    │  Pomodoro Timer │
    ╰─────────────────╯
        """
    
    def show_banner(self) -> None:
        """Show application banner"""
        banner_text = Text("🍅 LED Tomato CLI", style="bold red")
        subtitle = Text("Command-line Pomodoro Timer", style="dim")
        
        panel = Panel(
            Align.center(banner_text + "\n" + subtitle),
            box=box.DOUBLE,
            style="red"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_status(self, status: Dict[str, Any], device_ip: str) -> None:
        """Show device status"""
        # Create main status table
        table = Table(title="🍅 LED Tomato Status", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Device info
        table.add_row("Device IP", device_ip)
        table.add_row("Hostname", status.get('hostname', 'unknown'))
        table.add_row("WiFi Connected", "✅ Yes" if status.get('wifiConnected') else "❌ No")
        
        # Timer info
        pomodoro = status.get('pomodoro', {})
        state_names = {0: "Idle", 1: "Working", 2: "Short Break", 3: "Long Break"}
        state = pomodoro.get('state', 0)
        state_name = state_names.get(state, "Unknown")
        
        if state == 1:  # Working
            state_display = f"🔴 {state_name}"
        elif state in [2, 3]:  # Break
            state_display = f"🟢 {state_name}"
        else:  # Idle
            state_display = f"⚪ {state_name}"
        
        table.add_row("Timer State", state_display)
        table.add_row("Running", "✅ Yes" if pomodoro.get('running') else "❌ No")
        
        if pomodoro.get('running'):
            remaining = pomodoro.get('remaining', 0)
            elapsed = pomodoro.get('elapsed', 0)
            duration = pomodoro.get('duration', 0)
            
            table.add_row("Time Remaining", self._format_time(remaining))
            table.add_row("Time Elapsed", self._format_time(elapsed))
            table.add_row("Total Duration", self._format_time(duration))
            
            if duration > 0:
                progress = (elapsed / duration) * 100
                table.add_row("Progress", f"{progress:.1f}%")
        
        self.console.print(table)
    
    def show_timer_progress(self, status: Dict[str, Any]) -> None:
        """Show timer progress bar"""
        pomodoro = status.get('pomodoro', {})
        
        if not pomodoro.get('running'):
            return
        
        remaining = pomodoro.get('remaining', 0)
        elapsed = pomodoro.get('elapsed', 0)
        duration = pomodoro.get('duration', 0)
        state = pomodoro.get('state', 0)
        
        state_names = {1: "Work Session", 2: "Short Break", 3: "Long Break"}
        state_name = state_names.get(state, "Timer")
        
        if duration > 0:
            progress = elapsed / duration
            
            # Choose color based on session type
            if state == 1:  # Work
                color = "red"
            else:  # Break
                color = "green"
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.fields[session_type]}"),
                BarColumn(complete_style=color),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("[bold]{task.fields[remaining]}"),
                TimeRemainingColumn(),
                expand=True
            ) as progress_bar:
                
                task = progress_bar.add_task(
                    "timer",
                    total=duration,
                    completed=elapsed,
                    session_type=state_name,
                    remaining=self._format_time(remaining)
                )
                
                time.sleep(0.1)  # Brief pause to show the bar
    
    def show_device_list(self, devices: list) -> None:
        """Show discovered devices"""
        if not devices:
            self.console.print("[yellow]⚠️  No devices found[/yellow]")
            return
        
        table = Table(title="🔍 Discovered LED Tomato Devices", box=box.ROUNDED)
        table.add_column("IP Address", style="cyan")
        table.add_column("Hostname", style="white")
        table.add_column("Status", style="green")
        
        for device in devices:
            ip = device.get('ip', 'unknown')
            hostname = device.get('hostname', 'unknown')
            wifi_status = "📶 Connected" if device.get('wifi_connected') else "📶 AP Mode"
            
            table.add_row(ip, hostname, wifi_status)
        
        self.console.print(table)
    
    def show_config(self, config: Dict[str, Any]) -> None:
        """Show device configuration"""
        table = Table(title="⚙️ Device Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Timer settings
        work_time = config.get('workTime', 0) // 60
        short_break = config.get('shortBreakTime', 0) // 60
        long_break = config.get('longBreakTime', 0) // 60
        
        table.add_row("Work Time", f"{work_time} minutes")
        table.add_row("Short Break", f"{short_break} minutes")
        table.add_row("Long Break", f"{long_break} minutes")
        
        # Color settings
        work_color = f"#{config.get('workColor', 'FF0000')}"
        break_color = f"#{config.get('breakColor', '00FF00')}"
        
        table.add_row("Work Color", work_color)
        table.add_row("Break Color", break_color)
        
        # Animation settings
        work_anim = "✅ Enabled" if config.get('workAnimation') else "❌ Disabled"
        break_anim = "✅ Enabled" if config.get('breakAnimation') else "❌ Disabled"
        
        table.add_row("Work Animation", work_anim)
        table.add_row("Break Animation", break_anim)
        
        # Brightness
        brightness = config.get('brightness', 128)
        brightness_pct = (brightness / 255) * 100
        table.add_row("Brightness", f"{brightness} ({brightness_pct:.0f}%)")
        
        self.console.print(table)
    
    def show_session_complete(self, session_type: str, duration: int) -> None:
        """Show session completion message"""
        if session_type == "work":
            emoji = "🔴"
            message = f"Work session complete! ({duration} minutes)"
            style = "bold red"
        else:
            emoji = "🟢"
            message = f"Break time complete! ({duration} minutes)"
            style = "bold green"
        
        panel = Panel(
            Align.center(f"{emoji} {message}"),
            title="Session Complete",
            box=box.DOUBLE,
            style=style
        )
        
        self.console.print(panel)
        self.console.print("🔔 Time to switch activities!")
    
    def show_info(self, message: str) -> None:
        """Show info message"""
        self.console.print(f"[blue]ℹ️ {message}[/blue]")
    
    def show_success(self, message: str) -> None:
        """Show success message"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def show_warning(self, message: str) -> None:
        """Show warning message"""
        self.console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    def show_error(self, message: str) -> None:
        """Show error message"""
        self.console.print(f"[red]❌ {message}[/red]")

    def prompt_choice(self, question: str, choices: list, default: Optional[str] = None) -> str:
        """Prompt user for choice"""
        choice_text = " / ".join(choices)
        if default:
            prompt = f"{question} [{choice_text}] (default: {default}): "
        else:
            prompt = f"{question} [{choice_text}]: "
        
        while True:
            response = input(prompt).strip().lower()
            if not response and default:
                return default
            if response in [c.lower() for c in choices]:
                return response
            self.console.print(f"[red]Please choose from: {choice_text}[/red]")
    
    def prompt_confirm(self, question: str, default: bool = False) -> bool:
        """Prompt user for yes/no confirmation"""
        default_text = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_text}]: ").strip().lower()
        
        if not response:
            return default
        
        return response.startswith('y')
    
    def clear_screen(self) -> None:
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS"""
        if seconds < 0:
            seconds = 0
        
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def print_verbose(self, message: str) -> None:
        """Print message only in verbose mode"""
        if self.verbose:
            self.console.print(f"[dim]{message}[/dim]")
