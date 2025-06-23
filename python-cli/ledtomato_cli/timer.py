"""Timer management and monitoring for LED Tomato CLI"""

import asyncio
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Platform-specific imports
is_windows = sys.platform == 'win32'
if is_windows:
    import msvcrt  # Windows-specific for keyboard input
else:
    try:
        import termios
        import tty
        import select
    except ImportError:
        pass  # Might be running on a non-Unix-like platform without these modules

from .client import LEDTomatoClient
from .display import Display
from .config import Config
try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


class TimerManager:
    """Manages timer operations and monitoring"""
    
    def __init__(self, client: LEDTomatoClient, display: Display, config: Config):
        self.client = client
        self.display = display
        self.config = config
        self.running = False
        self.last_state = None
    
    def _kbhit(self) -> bool:
        """Platform-agnostic way to check for a keypress"""
        if is_windows:
            return msvcrt.kbhit()
        else:
            # Unix-like systems (Linux, macOS)
            try:
                # Check if there's data available to read on stdin
                # with a short timeout so it's non-blocking
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                return len(dr) > 0
            except (AttributeError, ValueError, NameError):
                # select or stdin might not be available in this environment
                return False
            except Exception:
                return False  # Any other exception, assume no key pressed
    
    def _getch(self) -> str:
        """Platform-agnostic way to get a keypress without blocking"""
        if is_windows:
            return msvcrt.getch().decode('utf-8', errors='ignore').lower()
        else:
            # Unix-like systems (Linux, macOS)
            try:
                if self._kbhit():
                    # Save terminal settings
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        # Set terminal to raw mode
                        tty.setraw(fd)
                        ch = sys.stdin.read(1)
                    finally:
                        # Restore terminal settings
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return ch.lower()
                return ''
            except (AttributeError, NameError, termios.error):
                # Modules or functions might not be available
                return ''
            except Exception:
                return ''  # Any other exception, return empty string
    
    async def interactive_loop(self) -> None:
        """Main interactive loop"""
        self.display.show_info("Interactive mode - Use commands or Ctrl+C to exit")
        self.display.console.print("\n[bold]Available commands:[/bold]")
        self.display.console.print("  [cyan]start[/cyan] - Start a timer session")
        self.display.console.print("  [cyan]cycle[/cyan] - Start continuous Pomodoro cycle")
        self.display.console.print("  [cyan]stop[/cyan] - Stop current session")
        self.display.console.print("  [cyan]status[/cyan] - Show current status")
        self.display.console.print("  [cyan]config[/cyan] - Show configuration")
        self.display.console.print("  [cyan]monitor[/cyan] - Monitor current session")
        self.display.console.print("  [cyan]quit[/cyan] - Exit application")
        self.display.console.print()
        
        while True:
            try:
                command = input("🍅 > ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    break
                elif command == 'start':
                    await self._interactive_start()
                elif command == 'cycle':
                    await self.start_pomodoro_cycle()
                elif command == 'stop':
                    await self._interactive_stop()
                elif command == 'status':
                    await self._show_status()
                elif command == 'config':
                    await self._show_config()
                elif command == 'monitor':
                    await self.monitor_session()
                elif command == 'help':
                    self._show_help()
                elif command == '':
                    continue
                else:
                    self.display.console.print(f"[red]Unknown command: {command}[/red]")
                    self.display.console.print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.display.show_error(f"Command failed: {e}")
    
    async def _interactive_start(self) -> None:
        """Interactive timer start"""
        # Check current status
        status = await self.client.get_status()
        if status and status.get('pomodoro', {}).get('running'):
            self.display.show_warning("Timer is already running!")
            return
        
        # Get timer type
        timer_type = self.display.prompt_choice(
            "Select timer type",
            ["work", "short", "long"],
            "work"
        )
        
        # Map to API type
        type_map = {"work": "work", "short": "short_break", "long": "long_break"}
        api_type = type_map[timer_type]
        
        # Ask for custom duration
        if self.display.prompt_confirm("Use custom duration?", False):
            try:
                duration = int(input("Duration in minutes: "))
                if duration > 0:
                    await self._set_custom_duration(timer_type, duration)
            except ValueError:
                self.display.show_error("Invalid duration")
                return
        
        # Start timer
        success = await self.client.start_timer(api_type)
        if success:
            timer_name = timer_type.replace('_', ' ').title()
            self.display.show_success(f"Started {timer_name} session")
            
            # Play start sound
            self._play_sound('start', timer_type)
            
            # Ask if user wants to monitor
            if self.display.prompt_confirm("Monitor this session?", True):
                await self.monitor_session()
        else:
            self.display.show_error("Failed to start timer")
    
    async def _interactive_stop(self) -> None:
        """Interactive timer stop with breathing yellow animation"""
        success = await self.client.stop_timer()
        if success:
            # Set breathing yellow animation for stopped state
            await self._set_breathing_yellow()
            self.display.show_success("Timer stopped (breathing yellow)")
        else:
            self.display.show_error("Failed to stop timer")
    
    async def _set_breathing_yellow(self) -> None:
        """Set LED to breathing yellow animation via REST API (stop state)"""
        config = await self.client.get_config()
        if not config:
            return
        config['workColor'] = 'FFFF00'  # Yellow
        config['workAnimation'] = True
        config['breakColor'] = 'FFFF00'
        config['breakAnimation'] = True
        await self.client.update_config(config)

    async def _restore_session_colors(self, session_type: str) -> None:
        """Restore LED color for work (red) or break (green) with animation as configured"""
        config = await self.client.get_config()
        if not config:
            return
        if session_type == 'work':
            config['workColor'] = 'FF0000'  # Red
            config['workAnimation'] = True
        else:
            config['breakColor'] = '00FF00'  # Green
            config['breakAnimation'] = True
        await self.client.update_config(config)

    async def _show_status(self) -> None:
        """Show current status"""
        status = await self.client.get_status()
        if status:
            self.display.show_status(status, self.client.host)
        else:
            self.display.show_error("Failed to get status")
    
    async def _show_config(self) -> None:
        """Show current configuration"""
        config = await self.client.get_config()
        if config:
            self.display.show_config(config)
        else:
            self.display.show_error("Failed to get configuration")
    
    def _show_help(self) -> None:
        """Show help information"""
        self.display.console.print("\n[bold]LED Tomato CLI Commands:[/bold]")
        self.display.console.print("  [cyan]start[/cyan]   - Start a Pomodoro timer session")
        self.display.console.print("  [cyan]stop[/cyan]    - Stop the current session")
        self.display.console.print("  [cyan]status[/cyan]  - Show device and timer status")
        self.display.console.print("  [cyan]config[/cyan]  - Show device configuration")
        self.display.console.print("  [cyan]monitor[/cyan] - Monitor current session with live updates")
        self.display.console.print("  [cyan]help[/cyan]    - Show this help message")
        self.display.console.print("  [cyan]quit[/cyan]    - Exit the application")
        self.display.console.print()
    async def monitor_session(self) -> None:
        """Monitor current timer session"""
        self.display.console.print("[blue]📊 Monitoring session... (Press 'q' to return to menu)[/blue]")
        
        try:
            while True:
                # Check for 'q' keypress to exit monitoring (non-blocking)
                if self._kbhit():
                    key = self._getch()
                    if key == 'q':
                        self.display.console.print("\n[yellow]Stopped monitoring[/yellow]")
                        return
                
                # Get the current status
                status = await self.client.get_status()
                if not status:
                    self.display.show_error("Lost connection to device")
                    break
                
                pomodoro = status.get('pomodoro', {})
                if not pomodoro.get('running'):
                    self.display.show_info("No active timer session")
                    break
                
                # Check for state changes
                current_state = pomodoro.get('state')
                if self.last_state != current_state and self.last_state is not None:
                    self._handle_state_change(current_state)
                self.last_state = current_state
                
                # Show progress
                self.display.show_timer_progress(status)
                
                # Check if session completed
                remaining = pomodoro.get('remaining', 0)
                if remaining == 0:
                    duration = pomodoro.get('duration', 0) // 60
                    state_names = {1: "work", 2: "short break", 3: "long break"}
                    session_type = state_names.get(current_state, "session")
                    
                    self.display.show_session_complete(session_type, duration)
                    self._play_sound('end', session_type)
                    break
                
                # Short sleep to avoid high CPU usage
                await asyncio.sleep(self.config.display.refresh_interval)
                
        except Exception as e:
            self.display.show_error(f"Monitoring error: {e}")
            # Return to menu instead of exiting completely
            return
    
    async def _set_custom_duration(self, timer_type: str, duration: int) -> None:
        """Set custom duration for timer type"""
        config = await self.client.get_config()
        if not config:
            return
        
        if timer_type == 'work':
            config['workTime'] = duration * 60
        elif timer_type == 'short':
            config['shortBreakTime'] = duration * 60
        elif timer_type == 'long':
            config['longBreakTime'] = duration * 60
        
        await self.client.update_config(config)
    
    def _handle_state_change(self, new_state: int) -> None:
        """Handle timer state change"""
        state_names = {0: "idle", 1: "work", 2: "short break", 3: "long break"}
        state_name = state_names.get(new_state, "unknown")
        
        self.display.show_info(f"Timer state changed to: {state_name}")
        
        # Play transition sound
        if new_state == 1:  # Work started
            self._play_sound('start', 'work')
        elif new_state in [2, 3]:  # Break started
            self._play_sound('start', 'break')
    
    def _play_sound(self, sound_type: str, session_type: str) -> None:
        """Play notification sound"""
        if not self.config.sound.enabled or not SOUND_AVAILABLE:
            return
        
        sound_file = None
        
        if sound_type == 'start':
            if session_type == 'work':
                sound_file = self.config.sound.work_start_sound
            else:  # break
                sound_file = self.config.sound.break_start_sound
        elif sound_type == 'end':
            sound_file = self.config.sound.session_end_sound
        
        if sound_file and sound_file.exists():
            try:
                playsound(str(sound_file))
            except Exception as e:
                self.display.print_verbose(f"Could not play sound: {e}")
    
    def log_session(self, session_type: str, duration: int, completed: bool) -> None:
        """Log completed session"""
        log_file = self.config.get_session_log_file()
        
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'type': session_type,
                'duration_minutes': duration,
                'completed': completed
            }
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(f"{log_entry}\n")                
        except Exception as e:
            self.display.print_verbose(f"Could not log session: {e}")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        log_file = self.config.get_session_log_file()
        stats = {
            'total_sessions': 0,
            'work_sessions': 0,
            'break_sessions': 0,
            'total_time_minutes': 0,
            'today_sessions': 0,
            'this_week_sessions': 0
        }
        
        if not log_file.exists():
            return stats
        
        try:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = eval(line.strip())  # Simple eval for dict parsing
                        session_date = datetime.fromisoformat(entry['timestamp']).date()
                        
                        stats['total_sessions'] += 1
                        stats['total_time_minutes'] += entry['duration_minutes']
                        
                        if entry['type'] == 'work':
                            stats['work_sessions'] += 1
                        else:
                            stats['break_sessions'] += 1
                        
                        if session_date == today:
                            stats['today_sessions'] += 1
                        
                        if session_date >= week_start:
                            stats['this_week_sessions'] += 1
                            
                    except Exception:
                        continue  # Skip malformed entries
                        
        except Exception as e:
            self.display.print_verbose(f"Could not read session log: {e}")
        
        return stats
    
    async def start_pomodoro_cycle(self) -> None:
        """Start a continuous Pomodoro cycle with automatic transitions"""
        self.display.show_info("🔄 Setting up continuous Pomodoro cycle")
        
        # Ask user if they want to use custom durations
        use_custom = self.display.prompt_confirm("Use custom durations for cycle?", False)
        
        custom_durations = {}
        if use_custom:
            try:
                # Format prompt with table
                self.display.console.print("[cyan]Please enter custom durations in minutes:[/cyan]")
                
                # Using input with validation
                work_duration = 0
                short_break_duration = 0
                long_break_duration = 0
                
                while work_duration <= 0:
                    try:
                        work_duration = int(input("Work session duration in minutes: "))
                        if work_duration <= 0:
                            self.display.show_error("Duration must be greater than 0")
                    except ValueError:
                        self.display.show_error("Please enter a valid number")
                
                while short_break_duration <= 0:
                    try:
                        short_break_duration = int(input("Short break duration in minutes: "))
                        if short_break_duration <= 0:
                            self.display.show_error("Duration must be greater than 0")
                    except ValueError:
                        self.display.show_error("Please enter a valid number")
                
                while long_break_duration <= 0:
                    try:
                        long_break_duration = int(input("Long break duration in minutes: "))
                        if long_break_duration <= 0:
                            self.display.show_error("Duration must be greater than 0")
                    except ValueError:
                        self.display.show_error("Please enter a valid number")
                
                custom_durations = {
                    'work': work_duration,
                    'short': short_break_duration,
                    'long': long_break_duration
                }
                
                # Update device configuration with custom durations
                config = await self.client.get_config()
                if config:
                    config['workTime'] = custom_durations['work'] * 60
                    config['shortBreakTime'] = custom_durations['short'] * 60
                    config['longBreakTime'] = custom_durations['long'] * 60
                    await self.client.update_config(config)
                    
                    # Create a visual confirmation
                    self.display.console.print("\n[bold green]✅ Custom Pomodoro durations set:[/bold green]")
                    self.display.console.print(f"  🔴 Work: [bold]{work_duration}[/bold] minutes")
                    self.display.console.print(f"  🟢 Short Break: [bold]{short_break_duration}[/bold] minutes")
                    self.display.console.print(f"  🟢 Long Break: [bold]{long_break_duration}[/bold] minutes")
                    self.display.console.print()
                else:
                    self.display.show_error("Failed to get configuration")
                    return
            except KeyboardInterrupt:
                self.display.show_warning("Custom duration setup cancelled")
                return
            except Exception as e:
                self.display.show_error(f"Error setting up custom durations: {e}")
                use_custom = False
        
        self.display.show_info("🔄 Starting continuous Pomodoro cycle (Press 'q' to stop)")
        self.display.console.print("[dim]The cycle will automatically transition between work and break sessions[/dim]")
        self.display.console.print("[dim]A long break will be taken after every 3 work sessions[/dim]")
        self.display.console.print("[dim]Press 'q' during any session to stop the cycle and return to menu[/dim]\n")
        
        work_sessions = 0
        try:
            while True:
                # Start work session
                await self._start_and_monitor('work', custom_durations if use_custom else None)
                work_sessions += 1
                
                # After work session, show progress
                self.display.console.print(f"[bold]Completed {work_sessions} work sessions[/bold]")
                
                # After 3 work sessions, take a long break
                if work_sessions % 3 == 0:
                    self.display.console.print("[cyan]Taking a long break...[/cyan]")
                    await self._start_and_monitor('long', custom_durations if use_custom else None)
                else:
                    self.display.console.print("[cyan]Taking a short break...[/cyan]")
                    await self._start_and_monitor('short', custom_durations if use_custom else None)
        except KeyboardInterrupt as e:
            # Check if this is our custom interruption from pressing 'q'
            if str(e) == "User requested to stop cycle with 'q' key":
                # Already handled in _start_and_monitor
                pass
            else:
                # This is an actual Ctrl+C
                self.display.console.print("\n[yellow]Stopped Pomodoro cycle with Ctrl+C[/yellow]")
                await self.client.stop_timer()
                # Set breathing yellow for stopped state
                await self._set_breathing_yellow()

    async def _start_and_monitor(self, session_type: str, custom_durations: dict = None) -> None:
        """Start a session (work/short/long) and monitor until it ends"""
        # Restore correct color before starting
        if session_type == 'work':
            await self._restore_session_colors('work')
        else:
            await self._restore_session_colors('break')
        
        # Apply custom duration for this session if provided
        if custom_durations and session_type in custom_durations:
            await self._set_custom_duration(session_type, custom_durations[session_type])
            
        type_map = {"work": "work", "short": "short_break", "long": "long_break"}
        api_type = type_map[session_type]
        success = await self.client.start_timer(api_type)
        if not success:
            self.display.show_error(f"Failed to start {session_type} session")
            return
        session_name = session_type.replace('_', ' ').title()
        self.display.show_success(f"Started {session_name} session")
        self._play_sound('start', session_type)
        
        # Monitor session
        self.display.console.print("[dim]Press 'q' to stop this session and cycle[/dim]")
        while True:
            # Check for 'q' keypress to exit monitoring (non-blocking)
            if self._kbhit():
                key = self._getch()
                if key == 'q':
                    self.display.console.print("\n[yellow]Session stopped early[/yellow]")
                    # Stop the timer
                    await self.client.stop_timer()
                    # Set breathing yellow for stopped state
                    await self._set_breathing_yellow()
                    # Re-raise KeyboardInterrupt to stop the cycle
                    raise KeyboardInterrupt("User requested to stop cycle with 'q' key")
            
            status = await self.client.get_status()
            if not status:
                self.display.show_error("Lost connection to device")
                return
            pomodoro = status.get('pomodoro', {})
            if not pomodoro.get('running'):
                self.display.show_info(f"{session_name} complete!")
                self._play_sound('end', session_type)
                break
            self.display.show_timer_progress(status)
            await asyncio.sleep(self.config.display.refresh_interval)
