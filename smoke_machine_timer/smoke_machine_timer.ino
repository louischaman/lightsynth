constexpr uint16_t onTimeMs {300U};
constexpr uint16_t offTimeMs {5000U};

constexpr uint8_t outputPin {5U};

void setup() 
{
    Serial.begin(115200);
    Serial.println("Start");

    pinMode(outputPin, OUTPUT);
    digitalWrite(outputPin, HIGH);

    // pinMode(outputPin, INPUT);
    // digitalWrite(outputPin, LOW);
}

void loop()
{
    Serial.println("on");
    // pinMode(outputPin, OUTPUT);
    digitalWrite(outputPin, LOW);
    delay(onTimeMs);
    
    Serial.println("off");
    // pinMode(outputPin, INPUT);
    digitalWrite(outputPin, HIGH);
    delay(offTimeMs);

}