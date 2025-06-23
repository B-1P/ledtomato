using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using System.Net.NetworkInformation;
using System.Net;
using System.Text;
using Newtonsoft.Json;
using System.Linq;
using System.Net.Sockets;

namespace LedTomatoWinUI
{
    public class LedColor
    {
        public int Red { get; set; }
        public int Green { get; set; }
        public int Blue { get; set; }

        public LedColor(int red, int green, int blue)
        {
            Red = Math.Clamp(red, 0, 255);
            Green = Math.Clamp(green, 0, 255);
            Blue = Math.Clamp(blue, 0, 255);
        }
    }

    public class EspDevice
    {
        public string Name { get; set; }
        public string IpAddress { get; set; }
        public bool IsConnected { get; set; }

        public EspDevice(string name, string ipAddress)
        {
            Name = name;
            IpAddress = ipAddress;
            IsConnected = false;
        }

        public override string ToString() => Name;
    }

    public class DeviceDiscoveredEventArgs : EventArgs
    {
        public EspDevice Device { get; }

        public DeviceDiscoveredEventArgs(EspDevice device)
        {
            Device = device;
        }
    }

    public class DeviceStatusChangedEventArgs : EventArgs
    {
        public EspDevice Device { get; }
        public bool IsConnected { get; }

        public DeviceStatusChangedEventArgs(EspDevice device, bool isConnected)
        {
            Device = device;
            IsConnected = isConnected;
        }
    }    public class DeviceStatus
    {
        public bool WifiConnected { get; set; }
        public string IpAddress { get; set; }
        public string Hostname { get; set; }
        public PomodoroStatus Pomodoro { get; set; }
    }

    public class PomodoroStatus
    {
        public int State { get; set; }
        public bool Running { get; set; }
        public int? Remaining { get; set; }
        public int? Elapsed { get; set; }
        public int? Duration { get; set; }
    }

    public class PomodoroConfig
    {
        public int WorkTime { get; set; }
        public int ShortBreakTime { get; set; }
        public int LongBreakTime { get; set; }
        public string WorkColor { get; set; }
        public string BreakColor { get; set; }
        public bool WorkAnimation { get; set; }
        public bool BreakAnimation { get; set; }
        public int Brightness { get; set; }
    }

    public class EspDeviceManager
    {
        private readonly HttpClient _httpClient;
        private readonly List<EspDevice> _discoveredDevices;
        private EspDevice _selectedDevice;

        public event EventHandler<DeviceDiscoveredEventArgs> DeviceDiscovered;
        public event EventHandler<DeviceStatusChangedEventArgs> DeviceStatusChanged;

        public EspDevice SelectedDevice => _selectedDevice;
        public IReadOnlyList<EspDevice> DiscoveredDevices => _discoveredDevices.AsReadOnly();

        public EspDeviceManager()
        {
            _httpClient = new HttpClient();
            _httpClient.Timeout = TimeSpan.FromSeconds(10);
            _discoveredDevices = new List<EspDevice>();
        }        public async Task DiscoverDevicesAsync()
        {
            try
            {
                // First try mDNS discovery (most reliable)
                await TryMdnsDiscoveryAsync();

                // Fallback to network scanning
                await ScanNetworkAsync();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Device discovery failed: {ex.Message}");
            }
        }

        private async Task TryMdnsDiscoveryAsync()
        {
            try
            {
                // Try to connect to ledtomato.local
                var device = await CheckLedTomatoDeviceAsync("ledtomato.local");
                if (device != null)
                {
                    lock (_discoveredDevices)
                    {
                        if (!_discoveredDevices.Any(d => d.IpAddress == device.IpAddress))
                        {
                            _discoveredDevices.Add(device);
                            DeviceDiscovered?.Invoke(this, new DeviceDiscoveredEventArgs(device));
                        }
                    }
                }
            }
            catch
            {
                // mDNS not available or device not found
            }
        }

        private async Task ScanNetworkAsync()
        {
            // Get local network range
            var localIp = GetLocalIPAddress();
            if (localIp == null) return;

            var networkPrefix = GetNetworkPrefix(localIp);
            var tasks = new List<Task>();

            // Scan common ESP32 IP range (192.168.x.1 to 192.168.x.254)
            for (int i = 1; i <= 254; i++)
            {
                var ip = $"{networkPrefix}.{i}";
                tasks.Add(CheckDeviceAsync(ip));
            }

            await Task.WhenAll(tasks);
        }        private async Task<EspDevice> CheckLedTomatoDeviceAsync(string hostOrIp)
        {
            try
            {
                // Try to connect to the status API endpoint
                var response = await _httpClient.GetAsync($"http://{hostOrIp}/api/status");
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var status = JsonConvert.DeserializeObject<DeviceStatus>(content);
                    
                    if (status != null && !string.IsNullOrEmpty(status.Hostname))
                    {
                        var actualIp = status.IpAddress ?? hostOrIp;
                        return new EspDevice($"LED Tomato ({status.Hostname})", actualIp);
                    }
                }
            }
            catch
            {
                // Device not reachable or not our ESP32
            }
            return null;
        }

        private async Task CheckDeviceAsync(string ipAddress)
        {
            try
            {
                // Try to ping first for quick filtering
                using (var ping = new Ping())
                {
                    var reply = await ping.SendPingAsync(ipAddress, 2000);
                    if (reply.Status != IPStatus.Success)
                        return;
                }

                var device = await CheckLedTomatoDeviceAsync(ipAddress);
                if (device != null)
                {
                    lock (_discoveredDevices)
                    {
                        if (!_discoveredDevices.Any(d => d.IpAddress == device.IpAddress))
                        {
                            _discoveredDevices.Add(device);
                            DeviceDiscovered?.Invoke(this, new DeviceDiscoveredEventArgs(device));
                        }
                    }
                }
            }
            catch
            {
                // Device not reachable or not our ESP32
            }
        }

        public void SelectDevice(EspDevice device)
        {
            if (_selectedDevice != null)
            {
                _selectedDevice.IsConnected = false;
                DeviceStatusChanged?.Invoke(this, new DeviceStatusChangedEventArgs(_selectedDevice, false));
            }

            _selectedDevice = device;
            
            if (_selectedDevice != null)
            {
                _selectedDevice.IsConnected = true;
                DeviceStatusChanged?.Invoke(this, new DeviceStatusChangedEventArgs(_selectedDevice, true));
            }
        }        public async Task<bool> TestConnectionAsync()
        {
            if (_selectedDevice == null) return false;

            try
            {
                var response = await _httpClient.GetAsync($"http://{_selectedDevice.IpAddress}/api/status");
                var isConnected = response.IsSuccessStatusCode;
                
                if (_selectedDevice.IsConnected != isConnected)
                {
                    _selectedDevice.IsConnected = isConnected;
                    DeviceStatusChanged?.Invoke(this, new DeviceStatusChangedEventArgs(_selectedDevice, isConnected));
                }
                
                return isConnected;
            }
            catch
            {
                if (_selectedDevice.IsConnected)
                {
                    _selectedDevice.IsConnected = false;
                    DeviceStatusChanged?.Invoke(this, new DeviceStatusChangedEventArgs(_selectedDevice, false));
                }
                return false;
            }
        }

        public async Task<DeviceStatus> GetStatusAsync()
        {
            if (_selectedDevice == null) return null;

            try
            {
                var response = await _httpClient.GetAsync($"http://{_selectedDevice.IpAddress}/api/status");
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<DeviceStatus>(content);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to get status: {ex.Message}");
            }
            return null;
        }

        public async Task<PomodoroConfig> GetConfigAsync()
        {
            if (_selectedDevice == null) return null;

            try
            {
                var response = await _httpClient.GetAsync($"http://{_selectedDevice.IpAddress}/api/pomodoro/config");
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<PomodoroConfig>(content);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to get config: {ex.Message}");
            }
            return null;
        }

        public async Task<bool> UpdateConfigAsync(PomodoroConfig config)
        {
            if (_selectedDevice == null) return false;

            try
            {
                var formData = new List<KeyValuePair<string, string>>
                {
                    new KeyValuePair<string, string>("workTime", config.WorkTime.ToString()),
                    new KeyValuePair<string, string>("shortBreakTime", config.ShortBreakTime.ToString()),
                    new KeyValuePair<string, string>("longBreakTime", config.LongBreakTime.ToString()),
                    new KeyValuePair<string, string>("workColor", config.WorkColor?.Replace("#", "") ?? "FF0000"),
                    new KeyValuePair<string, string>("breakColor", config.BreakColor?.Replace("#", "") ?? "00FF00"),
                    new KeyValuePair<string, string>("workAnimation", config.WorkAnimation.ToString().ToLower()),
                    new KeyValuePair<string, string>("breakAnimation", config.BreakAnimation.ToString().ToLower()),
                    new KeyValuePair<string, string>("brightness", config.Brightness.ToString())
                };

                var content = new FormUrlEncodedContent(formData);
                var response = await _httpClient.PostAsync($"http://{_selectedDevice.IpAddress}/api/pomodoro/config", content);
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to update config: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> StartTimerAsync(string timerType)
        {
            if (_selectedDevice == null) return false;

            try
            {
                var formData = new List<KeyValuePair<string, string>>
                {
                    new KeyValuePair<string, string>("type", timerType)
                };

                var content = new FormUrlEncodedContent(formData);
                var response = await _httpClient.PostAsync($"http://{_selectedDevice.IpAddress}/api/pomodoro/start", content);
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to start timer: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> StopTimerAsync()
        {
            if (_selectedDevice == null) return false;

            try
            {
                var response = await _httpClient.PostAsync($"http://{_selectedDevice.IpAddress}/api/pomodoro/stop", null);
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to stop timer: {ex.Message}");
                return false;
            }
        }        private string GetLocalIPAddress()
        {
            try
            {
                using (var socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, 0))
                {
                    socket.Connect("8.8.8.8", 65530);
                    var endPoint = socket.LocalEndPoint as IPEndPoint;
                    return endPoint?.Address.ToString();
                }
            }
            catch
            {
                return null;
            }
        }

        private string GetNetworkPrefix(string ipAddress)
        {
            var parts = ipAddress.Split('.');
            return $"{parts[0]}.{parts[1]}.{parts[2]}";
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
