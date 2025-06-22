export class DeviceService {
  static async discoverDevice(hostname) {
    try {
      // Try to resolve mDNS hostname
      const response = await fetch(`http://${hostname}/api/status`, {
        method: 'GET',
        timeout: 3000,
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.ipAddress;
      }
    } catch (error) {
      console.log('mDNS discovery failed:', error);
    }
    return null;
  }

  static async checkDevice(ip) {
    try {
      const response = await fetch(`http://${ip}/api/status`, {
        method: 'GET',
        timeout: 2000,
      });
      
      if (response.ok) {
        const data = await response.json();
        // Check if this is our LED Tomato device
        return data.hostname === 'ledtomato';
      }
    } catch (error) {
      // Device not responding
    }
    return false;
  }

  static async connect(ip) {
    try {
      const response = await fetch(`http://${ip}/api/status`, {
        method: 'GET',
        timeout: 5000,
      });
      
      return response.ok;
    } catch (error) {
      console.error('Connection failed:', error);
      return false;
    }
  }

  static async getStatus(ip) {
    try {
      const response = await fetch(`http://${ip}/api/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to get status:', error);
    }
    return null;
  }

  static async getConfig(ip) {
    try {
      const response = await fetch(`http://${ip}/api/pomodoro/config`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to get config:', error);
    }
    return null;
  }

  static async updateConfig(ip, config) {
    try {
      const formData = new FormData();
      formData.append('workTime', config.workTime.toString());
      formData.append('shortBreakTime', config.shortBreakTime.toString());
      formData.append('longBreakTime', config.longBreakTime.toString());
      formData.append('workColor', config.workColor.replace('#', ''));
      formData.append('breakColor', config.breakColor.replace('#', ''));
      formData.append('workAnimation', config.workAnimation.toString());
      formData.append('breakAnimation', config.breakAnimation.toString());
      formData.append('brightness', config.brightness.toString());

      const response = await fetch(`http://${ip}/api/pomodoro/config`, {
        method: 'POST',
        body: formData,
      });
      
      return response.ok;
    } catch (error) {
      console.error('Failed to update config:', error);
      return false;
    }
  }

  static async startPomodoro(ip, type) {
    try {
      const formData = new FormData();
      formData.append('type', type);

      const response = await fetch(`http://${ip}/api/pomodoro/start`, {
        method: 'POST',
        body: formData,
      });
      
      return response.ok;
    } catch (error) {
      console.error('Failed to start pomodoro:', error);
      return false;
    }
  }

  static async stopPomodoro(ip) {
    try {
      const response = await fetch(`http://${ip}/api/pomodoro/stop`, {
        method: 'POST',
      });
      
      return response.ok;
    } catch (error) {
      console.error('Failed to stop pomodoro:', error);
      return false;
    }
  }
}
