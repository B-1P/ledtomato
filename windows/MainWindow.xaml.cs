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
        private bool _isConnectedToDevice = false;        public MainWindow()
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
        }private void InitializeTimers()
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
            // Initialize UI with default values
            UpdateSliderTexts();
        }

        private void UpdateSliderTexts()
        {
            if (WorkDurationText != null)
                WorkDurationText.Text = $"{WorkDurationSlider.Value} min";
            if (BreakDurationText != null)
                BreakDurationText.Text = $"{BreakDurationSlider.Value} min";
        }

        private void InitializeEvents()
        {
            _pomodoroTimer.TimerTick += OnTimerTick;
            _pomodoroTimer.SessionCompleted += OnSessionCompleted;
            _pomodoroTimer.StateChanged += OnStateChanged;
            _pomodoroTimer.CycleAdvanced += OnCycleAdvanced;
            
            _deviceManager.DeviceDiscovered += OnDeviceDiscovered;
            _deviceManager.DeviceStatusChanged += OnDeviceStatusChanged;
        }

        private void UiTimer_Tick(object sender, object e)
        {
            UpdateUI();
        }        private async void StatusTimer_Tick(object sender, object e)
        {
            await UpdateDeviceStatus();
        }

        private async Task UpdateDeviceStatus()
        {
            if (_deviceManager.SelectedDevice != null)
            {
                _isConnectedToDevice = await _deviceManager.TestConnectionAsync();
                
                // Sync with device timer status if connected
                if (_isConnectedToDevice)
                {
                    var status = await _deviceManager.GetStatusAsync();
                    if (status?.Pomodoro != null && status.Pomodoro.Running && !_pomodoroTimer.IsRunning)
                    {
                        // Device timer is running but local timer isn't - this shouldn't happen in normal flow
                        // But we can handle it by syncing the local timer
                    }
                }
            }
        }

        private void UpdateUI()
        {
            // Update timer display
            var remaining = _pomodoroTimer.TimeRemaining;
            TimerDisplay.Text = $"{remaining.Minutes:D2}:{remaining.Seconds:D2}";
            
            // Update progress ring
            var progress = _pomodoroTimer.Progress;
            TimerProgressRing.Value = progress * 100;
            
            // Update session info
            var sessionType = _pomodoroTimer.CurrentSessionType switch
            {
                SessionType.Work => "Work",
                SessionType.ShortBreak => "Short Break",
                SessionType.LongBreak => "Long Break",
                _ => "Work"
            };
            SessionTypeText.Text = sessionType;
            SessionCountText.Text = $"Session {_pomodoroTimer.CompletedWorkSessions + 1}";
            
            // Update state
            StateText.Text = _pomodoroTimer.IsRunning ? "Running" : (_isConnectedToDevice ? "Ready" : "Not Connected");
            
            // Update buttons
            StartPauseButton.Content = _pomodoroTimer.IsRunning ? "Pause" : "Start";
            StartPauseButton.IsEnabled = _isConnectedToDevice;
            ResetButton.IsEnabled = _isConnectedToDevice;
        }        private async void OnTimerTick(object sender, EventArgs e)
        {
            // This is called from the local timer - we don't need to update ESP32 constantly
            // The ESP32 manages its own LED animations
            await Task.CompletedTask;
        }

        private async void OnSessionCompleted(object sender, SessionCompletedEventArgs e)
        {
            // Show completion notification
            var sessionName = e.SessionType switch
            {
                SessionType.Work => "Work",
                SessionType.ShortBreak => "Short Break",
                SessionType.LongBreak => "Long Break",
                _ => "Session"
            };

            var nextSession = _pomodoroTimer.CurrentSessionType switch
            {
                SessionType.Work => "work session",
                SessionType.ShortBreak => "short break",
                SessionType.LongBreak => "long break",
                _ => "next session"
            };

            var dialog = new ContentDialog()
            {
                Title = "Session Complete! 🍅",
                Content = $"{sessionName} completed! Time for a {nextSession}.",
                CloseButtonText = "OK",
                XamlRoot = this.Content.XamlRoot
            };
            
            await dialog.ShowAsync();
        }

        private void OnStateChanged(object sender, TimerStateChangedEventArgs e)
        {
            UpdateUI();
        }

        private void OnDeviceDiscovered(object sender, DeviceDiscoveredEventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                DeviceComboBox.Items.Add(e.Device);
                if (DeviceComboBox.SelectedItem == null)
                {
                    DeviceComboBox.SelectedItem = e.Device;
                    _deviceManager.SelectDevice(e.Device);
                }
            });
        }

        private void OnDeviceStatusChanged(object sender, DeviceStatusChangedEventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                DeviceStatusText.Text = e.IsConnected ? "Connected" : "Disconnected";
            });
        }

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

        private void DeviceComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.AddedItems.Count > 0 && e.AddedItems[0] is EspDevice device)
            {
                _deviceManager.SelectDevice(device);
            }
        }

        private async void RefreshDevicesButton_Click(object sender, RoutedEventArgs e)
        {
            DeviceComboBox.Items.Clear();
            await _deviceManager.DiscoverDevicesAsync();
        }        private async void WorkDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            if (_pomodoroTimer != null)
            {
                _pomodoroTimer.WorkDuration = TimeSpan.FromMinutes(e.NewValue);
                if (WorkDurationText != null)
                    WorkDurationText.Text = $"{e.NewValue} min";
                
                // Sync to device if connected
                await SyncConfigurationToDevice();
            }
        }

        private async void BreakDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            if (_pomodoroTimer != null)
            {
                _pomodoroTimer.ShortBreakDuration = TimeSpan.FromMinutes(e.NewValue);
                if (BreakDurationText != null)
                    BreakDurationText.Text = $"{e.NewValue} min";
                
                // Sync to device if connected
                await SyncConfigurationToDevice();
            }
        }

        private async void LongBreakDurationSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            if (_pomodoroTimer != null)
            {
                _pomodoroTimer.LongBreakDuration = TimeSpan.FromMinutes(e.NewValue);
                if (LongBreakDurationText != null)
                    LongBreakDurationText.Text = $"{e.NewValue} min";
                
                // Sync to device if connected
                await SyncConfigurationToDevice();
            }
        }

        private async void BrightnessSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            if (BrightnessText != null)
            {
                var percentage = (int)((e.NewValue / 255.0) * 100);
                BrightnessText.Text = $"{percentage}%";
            }
            
            // Sync to device if connected
            await SyncConfigurationToDevice();
        }

        private async void WorkAnimationCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            await SyncConfigurationToDevice();
        }

        private async void BreakAnimationCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            await SyncConfigurationToDevice();
        }

        private async void StartWorkButton_Click(object sender, RoutedEventArgs e)
        {
            await StartSpecificTimer(SessionType.Work);
        }

        private async void StartShortBreakButton_Click(object sender, RoutedEventArgs e)
        {
            await StartSpecificTimer(SessionType.ShortBreak);
        }

        private async void StartLongBreakButton_Click(object sender, RoutedEventArgs e)
        {
            await StartSpecificTimer(SessionType.LongBreak);
        }

        private async Task StartSpecificTimer(SessionType sessionType)
        {
            if (!_isConnectedToDevice)
            {
                var dialog = new ContentDialog()
                {
                    Title = "Device Not Connected",
                    Content = "Please connect to an ESP32 device first.",
                    CloseButtonText = "OK",
                    XamlRoot = this.Content.XamlRoot
                };
                await dialog.ShowAsync();
                return;
            }

            // Reset timer and set to specific session type
            _pomodoroTimer.Reset();
            _pomodoroTimer.SetSessionType(sessionType);

            // Update device configuration before starting
            await SyncConfigurationToDevice();
            
            // Start both local and device timers
            var timerType = sessionType switch
            {
                SessionType.Work => "work",
                SessionType.ShortBreak => "short_break",
                SessionType.LongBreak => "long_break",
                _ => "work"
            };
            
            var success = await _deviceManager.StartTimerAsync(timerType);
            if (success)
            {
                _pomodoroTimer.Start();
            }
            else
            {
                var dialog = new ContentDialog()
                {
                    Title = "Error",
                    Content = "Failed to start timer on device.",
                    CloseButtonText = "OK",
                    XamlRoot = this.Content.XamlRoot
                };
                await dialog.ShowAsync();
            }
        }

        private async Task SyncConfigurationToDevice()
        {
            if (!_isConnectedToDevice) return;

            var config = new PomodoroConfig
            {
                WorkTime = (int)_pomodoroTimer.WorkDuration.TotalSeconds,
                ShortBreakTime = (int)_pomodoroTimer.ShortBreakDuration.TotalSeconds,
                LongBreakTime = (int)_pomodoroTimer.LongBreakDuration.TotalSeconds,
                WorkColor = "FF0000", // Red for work
                BreakColor = "00FF00", // Green for break
                WorkAnimation = WorkAnimationCheckBox?.IsChecked ?? false,
                BreakAnimation = BreakAnimationCheckBox?.IsChecked ?? true,
                Brightness = (int)(BrightnessSlider?.Value ?? 128)
            };

            await _deviceManager.UpdateConfigAsync(config);
        }        private void AutoAdvanceCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (_pomodoroTimer != null)
            {
                _pomodoroTimer.AutoAdvanceBreaks = AutoAdvanceCheckBox?.IsChecked ?? false;
            }
        }

        private async void StartCycleButton_Click(object sender, RoutedEventArgs e)
        {
            if (!_isConnectedToDevice)
            {
                var dialog = new ContentDialog()
                {
                    Title = "Device Not Connected",
                    Content = "Please connect to an ESP32 device first.",
                    CloseButtonText = "OK",
                    XamlRoot = this.Content.XamlRoot
                };
                await dialog.ShowAsync();
                return;
            }

            // Start cycle mode
            _pomodoroTimer.CycleMode = true;
            
            // Update UI
            StartCycleButton.IsEnabled = false;
            StopCycleButton.IsEnabled = true;
            CycleStatusText.Text = "Cycle active - Starting with work session";
            
            // Disable individual session buttons during cycle
            var buttons = new[] { StartWorkButton, StartShortBreakButton, StartLongBreakButton };
            foreach (var button in buttons)
            {
                if (button != null) button.IsEnabled = false;
            }
            
            // Start with work session
            await StartSpecificTimer(SessionType.Work);
        }

        private async void StopCycleButton_Click(object sender, RoutedEventArgs e)
        {
            // Stop cycle mode
            _pomodoroTimer.CycleMode = false;
            _pomodoroTimer.Pause();
            
            // Stop device timer
            await _deviceManager.StopTimerAsync();
            
            // Update UI
            StartCycleButton.IsEnabled = true;
            StopCycleButton.IsEnabled = false;
            CycleStatusText.Text = "Cycle stopped";
            
            // Re-enable individual session buttons
            var buttons = new[] { StartWorkButton, StartShortBreakButton, StartLongBreakButton };
            foreach (var button in buttons)
            {
                if (button != null) button.IsEnabled = true;
            }
        }

        private async void OnCycleAdvanced(object sender, SessionType nextSessionType)
        {
            // Sync with ESP32 device for each session transition
            if (_isConnectedToDevice)
            {
                await SyncConfigurationToDevice();
                var timerType = nextSessionType switch
                {
                    SessionType.Work => "work",
                    SessionType.ShortBreak => "short_break",
                    SessionType.LongBreak => "long_break",
                    _ => "work"
                };
                await _deviceManager.StartTimerAsync(timerType);
            }
            // Update UI cycle status
            DispatcherQueue.TryEnqueue(() =>
            {
                var sessionName = nextSessionType switch
                {
                    SessionType.Work => "Work",
                    SessionType.ShortBreak => "Short Break",
                    SessionType.LongBreak => "Long Break",
                    _ => "Session"
                };
                CycleStatusText.Text = $"Cycle active - {sessionName} session";
            });
        }
    }
}
