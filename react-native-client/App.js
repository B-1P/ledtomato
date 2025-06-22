import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  Dimensions,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Sound from 'react-native-sound';
import PomodoroTimer from './components/PomodoroTimer';
import ConfigModal from './components/ConfigModal';
import ColorPicker from './components/ColorPicker';
import { DeviceService } from './services/DeviceService';
import { WindowsService } from './services/WindowsService';

const { width } = Dimensions.get('window');

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [deviceIP, setDeviceIP] = useState('');
  const [pomodoroState, setPomodoroState] = useState({
    running: false,
    state: 0, // 0: IDLE, 1: WORKING, 2: SHORT_BREAK, 3: LONG_BREAK
    remaining: 0,
    elapsed: 0,
    duration: 0,
  });
  const [config, setConfig] = useState({
    workTime: 25 * 60, // seconds
    shortBreakTime: 5 * 60,
    longBreakTime: 15 * 60,
    workColor: '#FF0000',
    breakColor: '#00FF00',
    workAnimation: false,
    breakAnimation: true,
    brightness: 128,
  });  const [showConfigModal, setShowConfigModal] = useState(false);
  const [currentSession, setCurrentSession] = useState(0);
  const [isWindowsPlatform, setIsWindowsPlatform] = useState(Platform.OS === 'windows');
  
  // Sound objects
  const [workSound, setWorkSound] = useState(null);
  const [breakSound, setBreakSound] = useState(null);
  useEffect(() => {
    initializeApp();
    loadSavedConfig();
    setupSounds();
    
    // Initialize Windows-specific features
    if (isWindowsPlatform) {
      WindowsService.enableWindowsFeatures();
    }
  }, []);

  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(checkStatus, 1000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const initializeApp = async () => {
    try {
      const savedIP = await AsyncStorage.getItem('deviceIP');
      if (savedIP) {
        setDeviceIP(savedIP);
        await connectToDevice(savedIP);
      } else {
        // Try to auto-discover device
        await discoverDevice();
      }
    } catch (error) {
      console.error('Error initializing app:', error);
    }
  };

  const setupSounds = () => {
    Sound.setCategory('Playback');
    
    // You would need to add these sound files to your project
    const workSnd = new Sound('work_start.mp3', Sound.MAIN_BUNDLE, (error) => {
      if (error) {
        console.log('Failed to load work sound', error);
      }
    });
    
    const breakSnd = new Sound('break_start.mp3', Sound.MAIN_BUNDLE, (error) => {
      if (error) {
        console.log('Failed to load break sound', error);
      }
    });
    
    setWorkSound(workSnd);
    setBreakSound(breakSnd);
  };

  const loadSavedConfig = async () => {
    try {
      const savedConfig = await AsyncStorage.getItem('pomodoroConfig');
      if (savedConfig) {
        setConfig(JSON.parse(savedConfig));
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const saveConfig = async (newConfig) => {
    try {
      await AsyncStorage.setItem('pomodoroConfig', JSON.stringify(newConfig));
      setConfig(newConfig);
      
      if (isConnected) {
        await DeviceService.updateConfig(deviceIP, newConfig);
      }
    } catch (error) {
      console.error('Error saving config:', error);
    }
  };

  const discoverDevice = async () => {
    try {
      // Try common mDNS name first
      const mdnsIP = await DeviceService.discoverDevice('ledtomato.local');
      if (mdnsIP) {
        await connectToDevice(mdnsIP);
        return;
      }
      
      // If mDNS fails, try to scan local network
      // This is a simplified version - you might want to implement proper network scanning
      const baseIP = '192.168.1.'; // Adjust based on your network
      for (let i = 1; i < 255; i++) {
        try {
          const testIP = baseIP + i;
          const response = await DeviceService.checkDevice(testIP);
          if (response) {
            await connectToDevice(testIP);
            return;
          }
        } catch (error) {
          // Continue searching
        }
      }
      
      Alert.alert('Device Not Found', 'Could not find LED Tomato device on the network');
    } catch (error) {
      console.error('Error discovering device:', error);
    }
  };

  const connectToDevice = async (ip) => {
    try {
      const connected = await DeviceService.connect(ip);
      if (connected) {
        setDeviceIP(ip);
        setIsConnected(true);
        await AsyncStorage.setItem('deviceIP', ip);
        
        // Load device configuration
        const deviceConfig = await DeviceService.getConfig(ip);
        if (deviceConfig) {
          setConfig(deviceConfig);
        }
      }
    } catch (error) {
      console.error('Error connecting to device:', error);
      setIsConnected(false);
    }
  };

  const checkStatus = async () => {
    try {
      const status = await DeviceService.getStatus(deviceIP);
      if (status && status.pomodoro) {
        const newState = status.pomodoro;
          // Check for state changes to play sounds
        if (pomodoroState.state !== newState.state && newState.running) {
          if (newState.state === 1) { // WORKING
            workSound?.play();
            
            // Show Windows toast notification
            if (isWindowsPlatform) {
              WindowsService.showToastNotification(
                'Work Session Started',
                `Focus time: ${formatTime(config.workTime)}`
              );
            }
          } else if (newState.state === 2 || newState.state === 3) { // BREAK
            breakSound?.play();
            
            // Show Windows toast notification
            if (isWindowsPlatform) {
              const breakType = newState.state === 2 ? 'Short Break' : 'Long Break';
              WindowsService.showToastNotification(
                `${breakType} Started`,
                'Time to relax and recharge!'
              );
            }
          }
        }
        
        setPomodoroState(newState);
      }
    } catch (error) {
      console.error('Error checking status:', error);
      setIsConnected(false);
    }
  };

  const startPomodoro = async (type) => {
    try {
      await DeviceService.startPomodoro(deviceIP, type);
      // Status will be updated by the polling function
    } catch (error) {
      Alert.alert('Error', 'Failed to start Pomodoro timer');
    }
  };

  const stopPomodoro = async () => {
    try {
      await DeviceService.stopPomodoro(deviceIP);
      // Status will be updated by the polling function
    } catch (error) {
      Alert.alert('Error', 'Failed to stop Pomodoro timer');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStateText = (state) => {
    switch (state) {
      case 0: return 'Ready';
      case 1: return 'Working';
      case 2: return 'Short Break';
      case 3: return 'Long Break';
      default: return 'Unknown';
    }
  };

  const getStateColor = (state) => {
    switch (state) {
      case 1: return config.workColor;
      case 2:
      case 3: return config.breakColor;
      default: return '#666';
    }
  };

  if (!isConnected) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f8f8f8" />
        <View style={styles.disconnectedContainer}>
          <Text style={styles.title}>🍅 LED Tomato</Text>
          <Text style={styles.subtitle}>Connecting to device...</Text>
          <TouchableOpacity
            style={styles.button}
            onPress={discoverDevice}>
            <Text style={styles.buttonText}>Scan for Device</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f8f8" />
      <ScrollView contentInsetAdjustmentBehavior="automatic">
        <View style={styles.header}>
          <Text style={styles.title}>🍅 LED Tomato</Text>
          <Text style={styles.subtitle}>Connected to {deviceIP}</Text>
        </View>

        <PomodoroTimer
          state={pomodoroState}
          config={config}
          onStart={startPomodoro}
          onStop={stopPomodoro}
          formatTime={formatTime}
          getStateText={getStateText}
          getStateColor={getStateColor}
        />

        <View style={styles.controlsContainer}>
          <TouchableOpacity
            style={[styles.controlButton, { backgroundColor: config.workColor }]}
            onPress={() => startPomodoro('work')}
            disabled={pomodoroState.running}>
            <Text style={styles.controlButtonText}>Start Work</Text>
            <Text style={styles.controlButtonSubtext}>{formatTime(config.workTime)}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, { backgroundColor: config.breakColor }]}
            onPress={() => startPomodoro('short_break')}
            disabled={pomodoroState.running}>
            <Text style={styles.controlButtonText}>Short Break</Text>
            <Text style={styles.controlButtonSubtext}>{formatTime(config.shortBreakTime)}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, { backgroundColor: config.breakColor }]}
            onPress={() => startPomodoro('long_break')}
            disabled={pomodoroState.running}>
            <Text style={styles.controlButtonText}>Long Break</Text>
            <Text style={styles.controlButtonSubtext}>{formatTime(config.longBreakTime)}</Text>
          </TouchableOpacity>
        </View>

        {pomodoroState.running && (
          <TouchableOpacity
            style={[styles.button, styles.stopButton]}
            onPress={stopPomodoro}>
            <Text style={styles.buttonText}>Stop Timer</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={[styles.button, styles.configButton]}
          onPress={() => setShowConfigModal(true)}>
          <Text style={styles.buttonText}>Settings</Text>
        </TouchableOpacity>

        <ConfigModal
          visible={showConfigModal}
          config={config}
          onSave={saveConfig}
          onClose={() => setShowConfigModal(false)}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f8f8',
    ...(Platform.OS === 'windows' && WindowsService.getWindowsSpecificStyles().container),
  },
  disconnectedContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 30,
    backgroundColor: '#fff',
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#d32f2f',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  controlsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  controlButton: {
    width: width / 2 - 30,
    paddingVertical: 20,
    paddingHorizontal: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  controlButtonSubtext: {
    color: '#fff',
    fontSize: 14,
    opacity: 0.8,
  },  button: {
    backgroundColor: '#d32f2f',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginHorizontal: 20,
    marginBottom: 15,
    alignItems: 'center',
    ...(Platform.OS === 'windows' && WindowsService.getWindowsSpecificStyles().button),
  },
  stopButton: {
    backgroundColor: '#f44336',
  },
  configButton: {
    backgroundColor: '#666',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default App;
