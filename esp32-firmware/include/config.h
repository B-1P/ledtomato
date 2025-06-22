#ifndef CONFIG_H
#define CONFIG_H

// Hardware Configuration
#define LED_PIN 5
#define LED_COUNT 30
#define LED_BRIGHTNESS 128

// WiFi Configuration
#define AP_SSID "LEDTomato-Setup"
#define AP_PASSWORD "pomodoro123"
#define HOSTNAME "ledtomato"

// Pomodoro Timer Defaults (in milliseconds)
#define DEFAULT_WORK_TIME 25 * 60 * 1000    // 25 minutes
#define DEFAULT_SHORT_BREAK 5 * 60 * 1000   // 5 minutes
#define DEFAULT_LONG_BREAK 15 * 60 * 1000   // 15 minutes

// LED Animation Settings
#define BREATHING_SPEED 20  // Lower = faster
#define BREATHING_MIN_BRIGHTNESS 10
#define BREATHING_MAX_BRIGHTNESS 255

// Debug
#define DEBUG_SERIAL 1

#endif
