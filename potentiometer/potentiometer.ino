/*

*/

unsigned long myTime;

void setup() {
  pinMode(A0,INPUT);
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  Serial.begin(9600);
}

void loop() {
  float p1 = analogRead(A0);
  float p2 = analogRead(A1);
  float p3 = analogRead(A2);
  float p4 = analogRead(A3);
  myTime = millis();
  Serial.println(String(myTime) + ',' + String(p4) + ',' + String(p3) + ',' + String(p2)  + ',' + String(p1));
  delay(100);
}
