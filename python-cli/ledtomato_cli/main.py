"""Main CLI entry point for LED Tomato"""

import asyncio
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .client import LEDTomatoClient
from .config import Config
from .discovery import DeviceDiscovery
from .display import Display
from .timer import TimerManager

console = Console()


@click.group(invoke_without_command=True)
@click.option('--device', '-d', help='Device IP address or hostname')
@click.option('--discover', is_flag=True, help='Auto-discover devices on network')
@click.option('--config', '-c', help='Path to config file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx: click.Context, device: Optional[str], discover: bool, config: Optional[str], verbose: bool) -> None:
    """🍅 LED Tomato - Command-line Pomodoro Timer Client
    
    Control your LED Tomato device from the command line.
    """
    ctx.ensure_object(dict)
    
    # Load configuration
    ctx.obj['config'] = Config.load(config)
    ctx.obj['verbose'] = verbose
    
    # Set up display
    ctx.obj['display'] = Display(verbose=verbose)
    
    if ctx.invoked_subcommand is None:
        # Show interactive mode if no subcommand
        asyncio.run(interactive_mode(device, discover, ctx.obj))


async def interactive_mode(device: Optional[str], discover: bool, ctx_obj: dict) -> None:
    """Interactive mode for LED Tomato CLI"""
    display = ctx_obj['display']
    config = ctx_obj['config']
    
    display.show_banner()
    
    # Discover or connect to device
    if discover or not device:
        discovery = DeviceDiscovery()
        device_ip = await discovery.find_device()
        if not device_ip:
            console.print("[red]❌ No LED Tomato devices found on network[/red]")
            sys.exit(1)
        device = device_ip
    
    # Create client
    client = LEDTomatoClient(device)
    
    try:
        # Test connection
        if not await client.ping():
            console.print(f"[red]❌ Could not connect to device at {device}[/red]")
            sys.exit(1)
        
        console.print(f"[green]✅ Connected to LED Tomato at {device}[/green]")
        
        # Start timer manager
        timer_manager = TimerManager(client, display, config)
        await timer_manager.interactive_loop()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--device', '-d', help='Device IP address or hostname')
@click.option('--type', '-t', type=click.Choice(['work', 'short', 'long']), default='work',
              help='Timer type (work, short break, long break)')
@click.option('--duration', type=int, help='Timer duration in minutes')
@click.pass_context
def start(ctx: click.Context, device: Optional[str], type: str, duration: Optional[int]) -> None:
    """Start a Pomodoro timer session"""
    asyncio.run(_start_timer(ctx, device, type, duration))


async def _start_timer(ctx: click.Context, device: Optional[str], timer_type: str, duration: Optional[int]) -> None:
    """Start timer implementation"""
    config = ctx.obj['config']
    display = ctx.obj['display']
    
    if not device:
        discovery = DeviceDiscovery()
        device = await discovery.find_device()
        if not device:
            console.print("[red]❌ No device found. Use --device to specify manually.[/red]")
            return
    
    client = LEDTomatoClient(device)
    
    if not await client.ping():
        console.print(f"[red]❌ Could not connect to device at {device}[/red]")
        return
    
    # Map timer type
    timer_map = {'work': 'work', 'short': 'short_break', 'long': 'long_break'}
    api_type = timer_map[timer_type]
    
    # Set custom duration if provided
    if duration:
        current_config = await client.get_config()
        if current_config:
            if timer_type == 'work':
                current_config['workTime'] = duration * 60
            elif timer_type == 'short':
                current_config['shortBreakTime'] = duration * 60
            elif timer_type == 'long':
                current_config['longBreakTime'] = duration * 60
            await client.update_config(current_config)
    
    # Start timer
    success = await client.start_timer(api_type)
    if success:
        timer_name = timer_type.replace('_', ' ').title()
        duration_text = f" ({duration} min)" if duration else ""
        console.print(f"[green]✅ Started {timer_name} session{duration_text}[/green]")
        
        # Monitor timer
        timer_manager = TimerManager(client, display, config)
        await timer_manager.monitor_session()
    else:
        console.print("[red]❌ Failed to start timer[/red]")


@cli.command()
@click.option('--device', '-d', help='Device IP address or hostname')
@click.pass_context
def stop(ctx: click.Context, device: Optional[str]) -> None:
    """Stop the current timer session"""
    asyncio.run(_stop_timer(ctx, device))


async def _stop_timer(ctx: click.Context, device: Optional[str]) -> None:
    """Stop timer implementation"""
    if not device:
        discovery = DeviceDiscovery()
        device = await discovery.find_device()
        if not device:
            console.print("[red]❌ No device found. Use --device to specify manually.[/red]")
            return
    
    client = LEDTomatoClient(device)
    
    if not await client.ping():
        console.print(f"[red]❌ Could not connect to device at {device}[/red]")
        return
    
    success = await client.stop_timer()
    if success:
        console.print("[green]✅ Timer stopped[/green]")
    else:
        console.print("[red]❌ Failed to stop timer[/red]")


@cli.command()
@click.option('--device', '-d', help='Device IP address or hostname')
@click.pass_context
def status(ctx: click.Context, device: Optional[str]) -> None:
    """Show current timer status"""
    asyncio.run(_show_status(ctx, device))


async def _show_status(ctx: click.Context, device: Optional[str]) -> None:
    """Show status implementation"""
    display = ctx.obj['display']
    
    if not device:
        discovery = DeviceDiscovery()
        device = await discovery.find_device()
        if not device:
            console.print("[red]❌ No device found. Use --device to specify manually.[/red]")
            return
    
    client = LEDTomatoClient(device)
    
    if not await client.ping():
        console.print(f"[red]❌ Could not connect to device at {device}[/red]")
        return
    
    status = await client.get_status()
    if status:
        display.show_status(status, device)
    else:
        console.print("[red]❌ Failed to get status[/red]")


@cli.command()
@click.pass_context
def discover(ctx: click.Context) -> None:
    """Discover LED Tomato devices on the network"""
    asyncio.run(_discover_devices(ctx))


async def _discover_devices(ctx: click.Context) -> None:
    """Discover devices implementation"""
    console.print("[blue]🔍 Scanning for LED Tomato devices...[/blue]")
    
    discovery = DeviceDiscovery()
    devices = await discovery.scan_network()
    
    if devices:
        console.print(f"[green]✅ Found {len(devices)} device(s):[/green]")
        for device in devices:
            console.print(f"  • {device['ip']} - {device['hostname']}")
    else:
        console.print("[yellow]⚠️  No LED Tomato devices found on network[/yellow]")


@cli.command()
@click.option('--device', '-d', help='Device IP address or hostname')
@click.option('--work-time', type=int, help='Work session duration (minutes)')
@click.option('--short-break', type=int, help='Short break duration (minutes)')
@click.option('--long-break', type=int, help='Long break duration (minutes)')
@click.option('--work-color', help='Work session color (hex)')
@click.option('--break-color', help='Break session color (hex)')
@click.option('--brightness', type=click.IntRange(0, 255), help='LED brightness (0-255)')
@click.pass_context
def config(ctx: click.Context, device: Optional[str], **kwargs) -> None:
    """Configure timer settings"""
    asyncio.run(_configure_device(ctx, device, kwargs))


async def _configure_device(ctx: click.Context, device: Optional[str], settings: dict) -> None:
    """Configure device implementation"""
    if not device:
        discovery = DeviceDiscovery()
        device = await discovery.find_device()
        if not device:
            console.print("[red]❌ No device found. Use --device to specify manually.[/red]")
            return
    
    client = LEDTomatoClient(device)
    
    if not await client.ping():
        console.print(f"[red]❌ Could not connect to device at {device}[/red]")
        return
    
    # Get current config
    current_config = await client.get_config()
    if not current_config:
        console.print("[red]❌ Failed to get current configuration[/red]")
        return
    
    # Update with new settings
    updated = False
    if settings['work_time']:
        current_config['workTime'] = settings['work_time'] * 60
        updated = True
    if settings['short_break']:
        current_config['shortBreakTime'] = settings['short_break'] * 60
        updated = True
    if settings['long_break']:
        current_config['longBreakTime'] = settings['long_break'] * 60
        updated = True
    if settings['work_color']:
        current_config['workColor'] = settings['work_color'].lstrip('#')
        updated = True
    if settings['break_color']:
        current_config['breakColor'] = settings['break_color'].lstrip('#')
        updated = True
    if settings['brightness'] is not None:
        current_config['brightness'] = settings['brightness']
        updated = True
    
    if updated:
        success = await client.update_config(current_config)
        if success:
            console.print("[green]✅ Configuration updated[/green]")
        else:
            console.print("[red]❌ Failed to update configuration[/red]")
    else:
        console.print("[yellow]⚠️  No settings provided to update[/yellow]")


if __name__ == '__main__':
    cli()
