/*
  AnalogReadSerial
  Number of Samples: 24
  Average Vgas: 274.56
  Average Vref: 273.12  
  Average Vtemp: 269.84

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

  int Sensitivity = 31;
  int TIAGain = 100;

  Vgas = TotVgas/NumOfSamples;
  Vref = TotVref/NumOfSamples;
  Vtemp = TotVtemp/NumOfSamples;

  float SenCalib = Sensitivity * TIAGain;
  Serial.println("SenCalib: " +String(SenCalib));

  float Concentration = (1000000 / SenCalib) * (Vgas - Vref);
  
  Serial.println("Average Vgas: " +String(TotVgas/NumOfSamples));
  Serial.println("Average Vref: " +String(TotVref/NumOfSamples));
  Serial.println("Average Vtemp: " +String(TotVtemp/NumOfSamples));
  Serial.println("Concentration: " +String(Concentration));
  Serial.println("Number of Samples: " +String(NumOfSamples));
  delay(1000);
  
  
}
