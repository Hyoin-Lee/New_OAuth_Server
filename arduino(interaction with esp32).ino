#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "JohnHughes - Vip 2.4GHz";
const char* password = "Qlalf2ek!@";
const char* mqttServer = "192.168.1.144";
const int mqttPort = 1883;
const char* mqttTopic = "control_led";

WiFiClient espClient;
PubSubClient client(espClient);

const int LED_PIN = 2;
bool ledState = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  connectToWiFi();
  connectToMQTT();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  
  // Convert byte message to string
  String messageStr = "";
  for (int i = 0; i < length; i++) {
    messageStr += (char)message[i];
  }
  Serial.println(messageStr);

  // Toggle LED state based on message content
  if (messageStr == "on") {
    ledState = true;
  } else if (messageStr == "off") {
    ledState = false;
  }

  // Update LED
  digitalWrite(LED_PIN, ledState ? HIGH : LOW);
}

void connectToWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 10) {
    delay(1000);
    Serial.println("Attempting to connect to Wi-Fi...");
    attempt++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to Wi-Fi!");
  }
}

void connectToMQTT() {
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  Serial.println("Attempting MQTT connection...");
  String clientId = "ESP32Client-" + String(random(0xffff), HEX);
  if (client.connect(clientId.c_str())) {
    Serial.println("Connected to MQTT broker!");
    client.subscribe(mqttTopic);
  } else {
    Serial.print("Failed to connect to MQTT broker, rc=");
    Serial.print(client.state());
    Serial.println(" Trying again in 5 seconds...");
    delay(5000);
  }
}

void reconnect() {
  while (!client.connected()) {
    connectToWiFi();
    connectToMQTT();
  }
}
