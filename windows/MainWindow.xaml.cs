using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Threading.Tasks;
using Microsoft.UI.Dispatching;

namespace LedTomatoWinUI
{
    public sealed partial class MainWindow : Window
    {
        private readonly PomodoroTimer _pomodoroTimer;
        private readonly EspDeviceManager _deviceManager;
        private DispatcherTimer _uiTimer;
        private DispatcherTimer _statusTimer;
        private bool _isConnectedToDevice = false;

        public MainWindow()
        {
            try
            {
                this.InitializeComponent();
                this.Title = "LED Tomato - Pomodoro Timer";
                
                _pomodoroTimer = new PomodoroTimer();
                _deviceManager = new EspDeviceManager();
                
                InitializeTimers();
                InitializeEvents();
                LoadSettings();
                
                // Start device discovery
                _ = Task.Run(async () => await _deviceManager.DiscoverDevicesAsync());
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"MainWindow initialization failed: {ex}");
                throw;
            }
        }

        private void InitializeTimers()
        {
            _uiTimer = new DispatcherTimer();
            _uiTimer.Interval = TimeSpan.FromSeconds(1);
            _uiTimer.Tick += UiTimer_Tick;
            _uiTimer.Start();

            _statusTimer = new DispatcherTimer();
            _statusTimer.Interval = TimeSpan.FromSeconds(5);
            _statusTimer.Tick += StatusTimer_Tick;
            _statusTimer.Start();
        }

        private void LoadSettings()
        {
            // Initialize UI with default values - minimal for now
            System.Diagnostics.Debug.WriteLine("Settings loaded");
        }

        private void InitializeEvents()
        {
            _pomodoroTimer.TimerTick += OnTimerTick;
            _pomodoroTimer.SessionCompleted += OnSessionCompleted;
            _pomodoroTimer.StateChanged += OnStateChanged;
            
            _deviceManager.DeviceDiscovered += OnDeviceDiscovered;
            _deviceManager.DeviceStatusChanged += OnDeviceStatusChanged;
        }

        private void UiTimer_Tick(object sender, object e)
        {
            UpdateUI();
        }

        private async void StatusTimer_Tick(object sender, object e)
        {
            await UpdateDeviceStatus();
        }

        private async Task UpdateDeviceStatus()
        {
            if (_deviceManager.SelectedDevice != null)
            {
                _isConnectedToDevice = await _deviceManager.TestConnectionAsync();
            }
        }

        private void UpdateUI()
        {
            // Update timer display - using debug output for now
            var remaining = _pomodoroTimer.TimeRemaining;
            var progress = _pomodoroTimer.Progress;
            var sessionType = _pomodoroTimer.CurrentSessionType switch
            {
                SessionType.Work => "Work",
                SessionType.ShortBreak => "Short Break",
                SessionType.LongBreak => "Long Break",
                _ => "Work"
            };
            
            // Debug output instead of UI updates for now
            System.Diagnostics.Debug.WriteLine($"Timer: {remaining.Minutes:D2}:{remaining.Seconds:D2} - {sessionType} - {(_pomodoroTimer.IsRunning ? "Running" : "Stopped")}");
        }

        private async void OnTimerTick(object sender, EventArgs e)
        {
            await Task.CompletedTask;
        }

        private void OnSessionCompleted(object sender, SessionCompletedEventArgs e)
        {
            // Simplified session completion handler to fix crashes
            DispatcherQueue.TryEnqueue(() =>
            {
                try
                {
                    var sessionName = e.SessionType switch
                    {
                        SessionType.Work => "Work",
                        SessionType.ShortBreak => "Short Break",
                        SessionType.LongBreak => "Long Break",
                        _ => "Session"
                    };

                    System.Diagnostics.Debug.WriteLine($"{sessionName} session completed!");

                    // Handle cycle mode - simplified
                    if (_pomodoroTimer.CycleMode)
                    {
                        // Auto-advance if enabled
                        if (_pomodoroTimer.AutoAdvanceBreaks || _pomodoroTimer.CurrentSessionType == SessionType.Work)
                        {
                            // Auto-start the next session after a short delay
                            Task.Run(async () =>
                            {
                                await Task.Delay(2000);
                                if (_pomodoroTimer.CycleMode)
                                {
                                    DispatcherQueue.TryEnqueue(() => _pomodoroTimer.Start());
                                }
                            });
                        }
                        return;
                    }

                    // For manual mode, just log completion - no dialog to avoid crashes
                    System.Diagnostics.Debug.WriteLine($"Session complete! Ready for next session.");
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error in OnSessionCompleted: {ex}");
                }
            });
        }

        private void OnStateChanged(object sender, TimerStateChangedEventArgs e)
        {
            UpdateUI();
        }

        private void OnDeviceDiscovered(object sender, DeviceDiscoveredEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Device discovered: {e.Device.Name}");
        }

        private void OnDeviceStatusChanged(object sender, DeviceStatusChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Device status: {(e.IsConnected ? "Connected" : "Disconnected")}");
        }

        // Simplified button handlers
        private void StartPauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_pomodoroTimer.IsRunning)
            {
                _pomodoroTimer.Pause();
            }
            else
            {
                _pomodoroTimer.Start();
            }
        }

        private void ResetButton_Click(object sender, RoutedEventArgs e)
        {
            _pomodoroTimer.Reset();
        }

        // Missing event handlers referenced by XAML
        private void DeviceComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Device selection changed");
        }

        private void RefreshDevicesButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Refresh devices clicked");
        }

        private void WorkDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Work duration changed to {e.NewValue}");
        }

        private void BreakDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Break duration changed to {e.NewValue}");
        }

        private void LongBreakDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Long break duration changed to {e.NewValue}");
        }

        private void BrightnessSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"Brightness changed to {e.NewValue}");
        }

        private void WorkAnimationCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Work animation setting changed");
        }

        private void BreakAnimationCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Break animation setting changed");
        }

        private void StartWorkButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Start work button clicked");
            _pomodoroTimer.SetSessionType(SessionType.Work);
            _pomodoroTimer.Start();
        }

        private void StartShortBreakButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Start short break button clicked");
            _pomodoroTimer.SetSessionType(SessionType.ShortBreak);
            _pomodoroTimer.Start();
        }

        private void StartLongBreakButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Start long break button clicked");
            _pomodoroTimer.SetSessionType(SessionType.LongBreak);
            _pomodoroTimer.Start();
        }

        private void StartCycleButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Start cycle button clicked");
            _pomodoroTimer.CycleMode = true;
            _pomodoroTimer.SetSessionType(SessionType.Work);
            _pomodoroTimer.Start();
        }

        private void StopCycleButton_Click(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Stop cycle button clicked");
            _pomodoroTimer.CycleMode = false;
            _pomodoroTimer.Pause();
        }

        private void AutoAdvanceCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("Auto advance setting changed");
            if (sender is CheckBox checkBox)
            {
                _pomodoroTimer.AutoAdvanceBreaks = checkBox.IsChecked ?? false;
            }
        }
    }
}
