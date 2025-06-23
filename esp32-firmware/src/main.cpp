#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <DNSServer.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <ESPmDNS.h>
#include <Adafruit_NeoPixel.h>
#include "config.h"

// Global objects
AsyncWebServer server(80);
DNSServer dnsServer;
Preferences preferences;
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// State variables
bool apMode = false;
bool wifiConnected = false;
String savedSSID = "";
String savedPassword = "";

// Pomodoro state
enum PomodoroState {
  IDLE,
  WORKING,
  SHORT_BREAK,
  LONG_BREAK
};

struct PomodoroConfig {
  unsigned long workTime = DEFAULT_WORK_TIME;
  unsigned long shortBreakTime = DEFAULT_SHORT_BREAK;
  unsigned long longBreakTime = DEFAULT_LONG_BREAK;
  uint32_t workColor = strip.Color(255, 0, 0);      // Red
  uint32_t breakColor = strip.Color(0, 255, 0);     // Green
  bool workAnimation = false;
  bool breakAnimation = true;
  uint8_t brightness = LED_BRIGHTNESS;
} pomodoroConfig;

struct PomodoroTimer {
  PomodoroState state = IDLE;
  unsigned long startTime = 0;
  unsigned long duration = 0;
  uint8_t session = 0;
  bool running = false;
} pomodoroTimer;

// LED Animation variables
unsigned long lastAnimationUpdate = 0;
float breathingPhase = 0;
bool breathingDirection = true;

// Function declarations
void setupWiFi();
void setupAP();
void setupWebServer();
void setupRoutes();
void handleRoot(AsyncWebServerRequest *request);
void handleWiFiConfig(AsyncWebServerRequest *request);
void handlePomodoroControl(AsyncWebServerRequest *request);
void handlePomodoroConfig(AsyncWebServerRequest *request);
void handleStatus(AsyncWebServerRequest *request);
void updateLEDs();
void breathingAnimation(uint32_t color);
void solidColor(uint32_t color);
uint32_t parseColor(String colorStr);
void savePomodoroConfig();
void loadPomodoroConfig();
void updatePomodoroTimer();

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("LED Tomato Pomodoro Timer Starting...");
  
  // Initialize preferences
  preferences.begin("ledtomato", false);
  
  // Initialize LED strip
  strip.begin();
  strip.setBrightness(LED_BRIGHTNESS);
  strip.show();
  
  // Load saved configuration
  loadPomodoroConfig();
  
  // Setup WiFi
  setupWiFi();
  
  // Setup web server
  setupWebServer();
  
  Serial.println("Setup complete!");
}

void loop() {
  if (apMode) {
    dnsServer.processNextRequest();
  }
  
  updatePomodoroTimer();
  updateLEDs();
  
  delay(50);
}

void setupWiFi() {
  // Load saved WiFi credentials
  savedSSID = preferences.getString("ssid", "");
  savedPassword = preferences.getString("password", "");
  
  if (savedSSID.length() > 0) {
    Serial.println("Attempting to connect to saved WiFi: " + savedSSID);
    WiFi.begin(savedSSID.c_str(), savedPassword.c_str());
    
    // Wait for connection for 10 seconds
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      wifiConnected = true;
      Serial.println();
      Serial.println("WiFi connected!");
      Serial.println("IP address: " + WiFi.localIP().toString());
      
      // Setup mDNS
      if (MDNS.begin(HOSTNAME)) {
        Serial.println("mDNS responder started: " + String(HOSTNAME) + ".local");
      }
      
      return;
    }
  }
  
  // Start AP mode if no saved credentials or connection failed
  setupAP();
}

void setupAP() {
  Serial.println("Starting AP mode...");
  apMode = true;
  
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.println("AP started: " + String(AP_SSID));
  Serial.println("AP IP address: " + WiFi.softAPIP().toString());
  
  // Setup DNS server for captive portal
  dnsServer.start(53, "*", WiFi.softAPIP());
}

void setupWebServer() {
  setupRoutes();
  server.begin();
  Serial.println("Web server started");
}

void setupRoutes() {
  // Serve static files for setup page
  server.on("/", HTTP_GET, handleRoot);
  
  // WiFi configuration endpoints
  server.on("/wifi-config", HTTP_POST, handleWiFiConfig);
  
  // Pomodoro control endpoints
  server.on("/api/pomodoro/start", HTTP_POST, handlePomodoroControl);
  server.on("/api/pomodoro/stop", HTTP_POST, handlePomodoroControl);
  server.on("/api/pomodoro/config", HTTP_GET, handlePomodoroConfig);
  server.on("/api/pomodoro/config", HTTP_POST, handlePomodoroConfig);
  server.on("/api/status", HTTP_GET, handleStatus);
  
  // CORS headers
  server.onNotFound([](AsyncWebServerRequest *request) {
    if (request->method() == HTTP_OPTIONS) {
      request->send(200);
    } else {
      request->send(404, "text/plain", "Not found");
    }
  });
  
  // Add CORS headers to all responses
  server.onNotFound([](AsyncWebServerRequest *request) {
    AsyncWebServerResponse *response = request->beginResponse(404, "text/plain", "Not found");
    response->addHeader("Access-Control-Allow-Origin", "*");
    response->addHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    response->addHeader("Access-Control-Allow-Headers", "Content-Type");
    request->send(response);
  });
}

void handleRoot(AsyncWebServerRequest *request) {
  String html = R"html(
<!DOCTYPE html>
<html>
<head>
    <title>LED Tomato Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 400px; margin: 0 auto; }
        h1 { color: #d32f2f; text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #d32f2f; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #b71c1c; }
        .status { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍅 LED Tomato</h1>
        <div class="status">
            <p>Connect to your WiFi network to control your Pomodoro timer</p>
        </div>
        <form action="/wifi-config" method="post">
            <input type="text" name="ssid" placeholder="WiFi Network Name" required>
            <input type="password" name="password" placeholder="WiFi Password" required>
            <button type="submit">Connect to WiFi</button>
        </form>
    </div>
</body>
</html>
)html";
  
  AsyncWebServerResponse *response = request->beginResponse(200, "text/html", html);
  response->addHeader("Access-Control-Allow-Origin", "*");
  request->send(response);
}

void handleWiFiConfig(AsyncWebServerRequest *request) {
  if (request->hasParam("ssid", true) && request->hasParam("password", true)) {
    String ssid = request->getParam("ssid", true)->value();
    String password = request->getParam("password", true)->value();
    
    // Save credentials
    preferences.putString("ssid", ssid);
    preferences.putString("password", password);
    
    String response = R"html(
<!DOCTYPE html>
<html>
<head>
    <title>LED Tomato - Connecting</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="15;url=http://ledtomato.local">
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; text-align: center; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 400px; margin: 0 auto; }
        h1 { color: #d32f2f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍅 LED Tomato</h1>
        <p>Connecting to WiFi...</p>
        <p>The device will restart and connect to your network.</p>
        <p>You can then access it at: <a href="http://ledtomato.local">ledtomato.local</a></p>
    </div>
</body>
</html>
)html";
    
    request->send(200, "text/html", response);
    
    // Restart after a delay
    delay(1000);
    ESP.restart();
  } else {
    request->send(400, "text/plain", "Missing parameters");
  }
}

void handlePomodoroControl(AsyncWebServerRequest *request) {
  String action = "";
  if (request->url() == "/api/pomodoro/start") {
    action = "start";
  } else if (request->url() == "/api/pomodoro/stop") {
    action = "stop";
  }
  
  DynamicJsonDocument doc(1024);
  
  if (action == "start") {
    if (request->hasParam("type", true)) {
      String type = request->getParam("type", true)->value();
      
      pomodoroTimer.running = true;
      pomodoroTimer.startTime = millis();
      
      if (type == "work") {
        pomodoroTimer.state = WORKING;
        pomodoroTimer.duration = pomodoroConfig.workTime;
      } else if (type == "short_break") {
        pomodoroTimer.state = SHORT_BREAK;
        pomodoroTimer.duration = pomodoroConfig.shortBreakTime;
      } else if (type == "long_break") {
        pomodoroTimer.state = LONG_BREAK;
        pomodoroTimer.duration = pomodoroConfig.longBreakTime;
      }
      
      doc["success"] = true;
      doc["message"] = "Pomodoro started";
    } else {
      doc["success"] = false;
      doc["message"] = "Missing type parameter";
    }
  } else if (action == "stop") {
    pomodoroTimer.running = false;
    pomodoroTimer.state = IDLE;
    doc["success"] = true;
    doc["message"] = "Pomodoro stopped";
  }
  
  String response;
  serializeJson(doc, response);
  
  AsyncWebServerResponse *resp = request->beginResponse(200, "application/json", response);
  resp->addHeader("Access-Control-Allow-Origin", "*");
  request->send(resp);
}

void handlePomodoroConfig(AsyncWebServerRequest *request) {
  DynamicJsonDocument doc(1024);
  
  if (request->method() == HTTP_GET) {
    // Return current configuration
    doc["workTime"] = pomodoroConfig.workTime / 1000;
    doc["shortBreakTime"] = pomodoroConfig.shortBreakTime / 1000;
    doc["longBreakTime"] = pomodoroConfig.longBreakTime / 1000;
    doc["workColor"] = String(pomodoroConfig.workColor, HEX);
    doc["breakColor"] = String(pomodoroConfig.breakColor, HEX);
    doc["workAnimation"] = pomodoroConfig.workAnimation;
    doc["breakAnimation"] = pomodoroConfig.breakAnimation;
    doc["brightness"] = pomodoroConfig.brightness;
  } else if (request->method() == HTTP_POST) {
    // Update configuration
    if (request->hasParam("workTime", true)) {
      pomodoroConfig.workTime = request->getParam("workTime", true)->value().toInt() * 1000;
    }
    if (request->hasParam("shortBreakTime", true)) {
      pomodoroConfig.shortBreakTime = request->getParam("shortBreakTime", true)->value().toInt() * 1000;
    }
    if (request->hasParam("longBreakTime", true)) {
      pomodoroConfig.longBreakTime = request->getParam("longBreakTime", true)->value().toInt() * 1000;
    }
    if (request->hasParam("workColor", true)) {
      pomodoroConfig.workColor = parseColor(request->getParam("workColor", true)->value());
    }
    if (request->hasParam("breakColor", true)) {
      pomodoroConfig.breakColor = parseColor(request->getParam("breakColor", true)->value());
    }
    if (request->hasParam("workAnimation", true)) {
      pomodoroConfig.workAnimation = request->getParam("workAnimation", true)->value() == "true";
    }
    if (request->hasParam("breakAnimation", true)) {
      pomodoroConfig.breakAnimation = request->getParam("breakAnimation", true)->value() == "true";
    }
    if (request->hasParam("brightness", true)) {
      pomodoroConfig.brightness = request->getParam("brightness", true)->value().toInt();
      strip.setBrightness(pomodoroConfig.brightness);
    }
    
    savePomodoroConfig();
    doc["success"] = true;
    doc["message"] = "Configuration updated";
  }
  
  String response;
  serializeJson(doc, response);
  
  AsyncWebServerResponse *resp = request->beginResponse(200, "application/json", response);
  resp->addHeader("Access-Control-Allow-Origin", "*");
  request->send(resp);
}

void handleStatus(AsyncWebServerRequest *request) {
  DynamicJsonDocument doc(1024);
  
  doc["wifiConnected"] = wifiConnected;
  doc["ipAddress"] = wifiConnected ? WiFi.localIP().toString() : WiFi.softAPIP().toString();
  doc["hostname"] = HOSTNAME;
  doc["pomodoro"]["state"] = pomodoroTimer.state;
  doc["pomodoro"]["running"] = pomodoroTimer.running;
  
  if (pomodoroTimer.running) {
    unsigned long elapsed = millis() - pomodoroTimer.startTime;
    unsigned long remaining = pomodoroTimer.duration > elapsed ? pomodoroTimer.duration - elapsed : 0;
    doc["pomodoro"]["remaining"] = remaining / 1000;
    doc["pomodoro"]["elapsed"] = elapsed / 1000;
    doc["pomodoro"]["duration"] = pomodoroTimer.duration / 1000;
  }
  
  String response;
  serializeJson(doc, response);
  
  AsyncWebServerResponse *resp = request->beginResponse(200, "application/json", response);
  resp->addHeader("Access-Control-Allow-Origin", "*");
  request->send(resp);
}

void updateLEDs() {
  if (pomodoroTimer.running) {
    uint32_t color;
    bool useAnimation;
    
    if (pomodoroTimer.state == WORKING) {
      color = pomodoroConfig.workColor;
      useAnimation = pomodoroConfig.workAnimation;
    } else {
      color = pomodoroConfig.breakColor;
      useAnimation = pomodoroConfig.breakAnimation;
    }
    
    if (useAnimation) {
      breathingAnimation(color);
    } else {
      solidColor(color);
    }
  } else {
    // Idle state - breathing orange
    breathingAnimation(strip.Color(255, 128, 0)); // Orange
  }
}

void breathingAnimation(uint32_t color) {
  if (millis() - lastAnimationUpdate > BREATHING_SPEED) {
    lastAnimationUpdate = millis();
    
    if (breathingDirection) {
      breathingPhase += 0.05;
      if (breathingPhase >= 1.0) {
        breathingPhase = 1.0;
        breathingDirection = false;
      }
    } else {
      breathingPhase -= 0.05;
      if (breathingPhase <= 0.0) {
        breathingPhase = 0.0;
        breathingDirection = true;
      }
    }
    
    // Calculate brightness based on sine wave
    float intensity = (sin(breathingPhase * PI) + 1.0) / 2.0;
    intensity = BREATHING_MIN_BRIGHTNESS + (BREATHING_MAX_BRIGHTNESS - BREATHING_MIN_BRIGHTNESS) * intensity;
    
    // Extract RGB components
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    
    // Apply intensity
    r = (r * intensity) / 255;
    g = (g * intensity) / 255;
    b = (b * intensity) / 255;
    
    uint32_t dimmedColor = strip.Color(r, g, b);
    
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, dimmedColor);
    }
    strip.show();
  }
}

void solidColor(uint32_t color) {
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

uint32_t parseColor(String colorStr) {
  // Remove # if present
  if (colorStr.startsWith("#")) {
    colorStr = colorStr.substring(1);
  }
  
  // Parse hex color
  long color = strtol(colorStr.c_str(), NULL, 16);
  uint8_t r = (color >> 16) & 0xFF;
  uint8_t g = (color >> 8) & 0xFF;
  uint8_t b = color & 0xFF;
  
  return strip.Color(r, g, b);
}

void savePomodoroConfig() {
  preferences.putULong("workTime", pomodoroConfig.workTime);
  preferences.putULong("shortBreak", pomodoroConfig.shortBreakTime);
  preferences.putULong("longBreak", pomodoroConfig.longBreakTime);
  preferences.putULong("workColor", pomodoroConfig.workColor);
  preferences.putULong("breakColor", pomodoroConfig.breakColor);
  preferences.putBool("workAnim", pomodoroConfig.workAnimation);
  preferences.putBool("breakAnim", pomodoroConfig.breakAnimation);
  preferences.putUChar("brightness", pomodoroConfig.brightness);
}

void loadPomodoroConfig() {
  pomodoroConfig.workTime = preferences.getULong("workTime", DEFAULT_WORK_TIME);
  pomodoroConfig.shortBreakTime = preferences.getULong("shortBreak", DEFAULT_SHORT_BREAK);
  pomodoroConfig.longBreakTime = preferences.getULong("longBreak", DEFAULT_LONG_BREAK);
  pomodoroConfig.workColor = preferences.getULong("workColor", strip.Color(255, 0, 0));
  pomodoroConfig.breakColor = preferences.getULong("breakColor", strip.Color(0, 255, 0));
  pomodoroConfig.workAnimation = preferences.getBool("workAnim", false);
  pomodoroConfig.breakAnimation = preferences.getBool("breakAnim", true);
  pomodoroConfig.brightness = preferences.getUChar("brightness", LED_BRIGHTNESS);
  
  strip.setBrightness(pomodoroConfig.brightness);
}

void updatePomodoroTimer() {
  if (pomodoroTimer.running) {
    unsigned long elapsed = millis() - pomodoroTimer.startTime;
    
    if (elapsed >= pomodoroTimer.duration) {
      // Timer finished
      pomodoroTimer.running = false;
      pomodoroTimer.state = IDLE;
      
      // Flash LEDs to indicate completion
      for (int i = 0; i < 3; i++) {
        solidColor(strip.Color(255, 255, 255));
        delay(200);
        solidColor(strip.Color(0, 0, 0));
        delay(200);
      }
    }
  }
}
