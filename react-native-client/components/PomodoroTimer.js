import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Animated,
} from 'react-native';

const { width } = Dimensions.get('window');

const PomodoroTimer = ({ state, config, formatTime, getStateText, getStateColor }) => {
  const progress = state.duration > 0 ? (state.duration - state.remaining) / state.duration : 0;
  const circumference = 2 * Math.PI * 80;
  const strokeDashoffset = circumference * (1 - progress);

  return (
    <View style={styles.container}>
      <View style={styles.timerContainer}>
        {/* Circular Progress */}
        <View style={styles.circularProgress}>
          <View style={[styles.circle, { borderColor: getStateColor(state.state) }]}>
            <Text style={styles.timeText}>
              {state.running ? formatTime(state.remaining) : '00:00'}
            </Text>
            <Text style={[styles.stateText, { color: getStateColor(state.state) }]}>
              {getStateText(state.state)}
            </Text>
          </View>
          
          {/* Progress Ring */}
          {state.running && (
            <View style={styles.progressRing}>
              <View 
                style={[
                  styles.progressFill,
                  { 
                    transform: [{ rotate: `${progress * 360}deg` }],
                    backgroundColor: getStateColor(state.state),
                  }
                ]} 
              />
            </View>
          )}
        </View>

        {/* Session Info */}
        <View style={styles.sessionInfo}>
          <Text style={styles.sessionText}>
            {state.running ? `Session ${Math.floor(state.elapsed / 60)} min` : 'Ready to start'}
          </Text>
          {state.duration > 0 && (
            <Text style={styles.progressText}>
              {Math.round(progress * 100)}% complete
            </Text>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 15,
    padding: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  timerContainer: {
    alignItems: 'center',
  },
  circularProgress: {
    position: 'relative',
    marginBottom: 20,
  },
  circle: {
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
  },
  progressRing: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: 200,
    height: 200,
    borderRadius: 100,
    overflow: 'hidden',
  },
  progressFill: {
    position: 'absolute',
    top: -100,
    left: 98,
    width: 4,
    height: 100,
    transformOrigin: '2px 100px',
  },
  timeText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  stateText: {
    fontSize: 16,
    fontWeight: '600',
  },
  sessionInfo: {
    alignItems: 'center',
  },
  sessionText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  progressText: {
    fontSize: 14,
    color: '#999',
  },
});

export default PomodoroTimer;
