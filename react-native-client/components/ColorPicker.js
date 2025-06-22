import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
} from 'react-native';
import Modal from 'react-native-modal';

const { width } = Dimensions.get('window');

const ColorPicker = ({ visible, color, onColorChange, onClose }) => {
  const [selectedColor, setSelectedColor] = useState(color);

  const predefinedColors = [
    '#FF0000', '#FF4500', '#FF8C00', '#FFD700',
    '#ADFF2F', '#32CD32', '#00FF00', '#00FF7F',
    '#00FFFF', '#1E90FF', '#0000FF', '#4169E1',
    '#8A2BE2', '#9400D3', '#FF00FF', '#FF1493',
    '#FF69B4', '#FFC0CB', '#FFFFFF', '#C0C0C0',
    '#808080', '#404040', '#000000', '#8B4513',
  ];

  const handleColorSelect = (newColor) => {
    setSelectedColor(newColor);
  };

  const handleSave = () => {
    onColorChange(selectedColor);
    onClose();
  };

  return (
    <Modal
      isVisible={visible}
      onBackdropPress={onClose}
      style={styles.modal}
    >
      <View style={styles.container}>
        <Text style={styles.title}>Choose Color</Text>
        
        <View style={styles.colorGrid}>
          {predefinedColors.map((colorOption, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.colorOption,
                { backgroundColor: colorOption },
                selectedColor === colorOption && styles.selectedColor,
              ]}
              onPress={() => handleColorSelect(colorOption)}
            />
          ))}
        </View>

        <View style={styles.preview}>
          <Text style={styles.previewLabel}>Selected Color:</Text>
          <View style={[styles.previewColor, { backgroundColor: selectedColor }]}>
            <Text style={styles.previewText}>{selectedColor}</Text>
          </View>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>Select</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modal: {
    margin: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    width: width - 40,
    maxWidth: 400,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  colorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  colorOption: {
    width: 45,
    height: 45,
    borderRadius: 22.5,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#ddd',
  },
  selectedColor: {
    borderColor: '#333',
    borderWidth: 3,
  },
  preview: {
    alignItems: 'center',
    marginBottom: 20,
  },
  previewLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  previewColor: {
    width: 100,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 12,
    marginRight: 10,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
  },
  saveButton: {
    flex: 1,
    paddingVertical: 12,
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

export default ColorPicker;
