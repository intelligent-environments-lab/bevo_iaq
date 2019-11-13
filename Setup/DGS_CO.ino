/*
  AnalogReadSerial
*/

  float TotVgas = 0;
  float TotVref = 0;
  float TotVtemp = 0;
  int NumOfSamples = 0;
  
void setup(){
  Serial.begin(9600);
}  

void loop(){
  float Vgas = analogRead(A0);
  float Vref = analogRead(A1);
  float Vtemp = analogRead(A2);
  
  TotVgas +=Vgas;
  TotVref +=Vref;
  TotVtemp += Vtemp;
  NumOfSamples++;
  
  Serial.println("Average Vgas: " +String(TotVgas/NumOfSamples));
  Serial.println("Average Vref: " +String(TotVref/NumOfSamples));
  Serial.println("Average Vtemp: " +String(TotVtemp/NumOfSamples));
  Serial.println("Number of Samples: " +String(NumOfSamples));
  //delay(1000);
  
}
