import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Switch,
  StyleSheet,
  ScrollView,
} from 'react-native';
import Modal from 'react-native-modal';
import Slider from '@react-native-community/slider';
import ColorPicker from './ColorPicker';

const ConfigModal = ({ visible, config, onSave, onClose }) => {
  const [localConfig, setLocalConfig] = useState(config);
  const [showWorkColorPicker, setShowWorkColorPicker] = useState(false);
  const [showBreakColorPicker, setShowBreakColorPicker] = useState(false);

  const updateConfig = (key, value) => {
    setLocalConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    onSave(localConfig);
    onClose();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    return `${mins} min`;
  };

  return (
    <Modal
      isVisible={visible}
      onBackdropPress={onClose}
      style={styles.modal}
    >
      <View style={styles.container}>
        <Text style={styles.title}>Pomodoro Settings</Text>
        
        <ScrollView style={styles.content}>
          {/* Timer Settings */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Timer Duration</Text>
            
            <View style={styles.sliderContainer}>
              <Text style={styles.label}>Work Time: {formatTime(localConfig.workTime)}</Text>
              <Slider
                style={styles.slider}
                minimumValue={300} // 5 minutes
                maximumValue={3600} // 60 minutes
                step={300} // 5 minute steps
                value={localConfig.workTime}
                onValueChange={(value) => updateConfig('workTime', value)}
                minimumTrackTintColor="#d32f2f"
                maximumTrackTintColor="#ddd"
              />
            </View>

            <View style={styles.sliderContainer}>
              <Text style={styles.label}>Short Break: {formatTime(localConfig.shortBreakTime)}</Text>
              <Slider
                style={styles.slider}
                minimumValue={180} // 3 minutes
                maximumValue={900} // 15 minutes
                step={60} // 1 minute steps
                value={localConfig.shortBreakTime}
                onValueChange={(value) => updateConfig('shortBreakTime', value)}
                minimumTrackTintColor="#4caf50"
                maximumTrackTintColor="#ddd"
              />
            </View>

            <View style={styles.sliderContainer}>
              <Text style={styles.label}>Long Break: {formatTime(localConfig.longBreakTime)}</Text>
              <Slider
                style={styles.slider}
                minimumValue={600} // 10 minutes
                maximumValue={1800} // 30 minutes
                step={300} // 5 minute steps
                value={localConfig.longBreakTime}
                onValueChange={(value) => updateConfig('longBreakTime', value)}
                minimumTrackTintColor="#4caf50"
                maximumTrackTintColor="#ddd"
              />
            </View>
          </View>

          {/* LED Settings */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>LED Settings</Text>
            
            <View style={styles.sliderContainer}>
              <Text style={styles.label}>Brightness: {Math.round((localConfig.brightness / 255) * 100)}%</Text>
              <Slider
                style={styles.slider}
                minimumValue={25}
                maximumValue={255}
                step={10}
                value={localConfig.brightness}
                onValueChange={(value) => updateConfig('brightness', value)}
                minimumTrackTintColor="#ff9800"
                maximumTrackTintColor="#ddd"
              />
            </View>

            <View style={styles.colorSection}>
              <Text style={styles.label}>Work Color</Text>
              <TouchableOpacity
                style={[styles.colorButton, { backgroundColor: localConfig.workColor }]}
                onPress={() => setShowWorkColorPicker(true)}
              >
                <Text style={styles.colorButtonText}>{localConfig.workColor}</Text>
              </TouchableOpacity>
              
              <View style={styles.switchContainer}>
                <Text style={styles.switchLabel}>Work Animation</Text>
                <Switch
                  value={localConfig.workAnimation}
                  onValueChange={(value) => updateConfig('workAnimation', value)}
                  trackColor={{ false: '#ddd', true: '#d32f2f' }}
                />
              </View>
            </View>

            <View style={styles.colorSection}>
              <Text style={styles.label}>Break Color</Text>
              <TouchableOpacity
                style={[styles.colorButton, { backgroundColor: localConfig.breakColor }]}
                onPress={() => setShowBreakColorPicker(true)}
              >
                <Text style={styles.colorButtonText}>{localConfig.breakColor}</Text>
              </TouchableOpacity>
              
              <View style={styles.switchContainer}>
                <Text style={styles.switchLabel}>Break Animation</Text>
                <Switch
                  value={localConfig.breakAnimation}
                  onValueChange={(value) => updateConfig('breakAnimation', value)}
                  trackColor={{ false: '#ddd', true: '#4caf50' }}
                />
              </View>
            </View>
          </View>
        </ScrollView>

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>Save</Text>
          </TouchableOpacity>
        </View>

        {/* Color Pickers */}
        <ColorPicker
          visible={showWorkColorPicker}
          color={localConfig.workColor}
          onColorChange={(color) => updateConfig('workColor', color)}
          onClose={() => setShowWorkColorPicker(false)}
        />

        <ColorPicker
          visible={showBreakColorPicker}
          color={localConfig.breakColor}
          onColorChange={(color) => updateConfig('breakColor', color)}
          onClose={() => setShowBreakColorPicker(false)}
        />
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modal: {
    margin: 0,
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  sliderContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  slider: {
    height: 40,
  },
  colorSection: {
    marginBottom: 20,
  },
  colorButton: {
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 10,
  },
  colorButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
  },
  switchLabel: {
    fontSize: 16,
    color: '#666',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 15,
    marginRight: 10,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
  },
  saveButton: {
    flex: 1,
    paddingVertical: 15,
    marginLeft: 10,
    borderRadius: 8,
    backgroundColor: '#d32f2f',
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ConfigModal;
