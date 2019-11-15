#include <SoftwareSerial.h>

/*
  AnalogReadSerial
  Number of Samples: 24
  Average Vgas: 274.56
  Average Vref: 273.12  
  Average Vtemp: 269.84

*/

  // O3
  const int RX1 = 0;
  const int TX1 = 1;
  SoftwareSerial SoftSerialOne(RX1,TX1);
  float TotVgas_o3 = 0;
  float TotVref_o3 = 0;
  float TotVtemp_o3 = 0;
  
  // CO
  const int RX2 = 2;
  const int TX2 = 3;
  SoftwareSerial SoftSerialTwo(RX2,TX2);
  float TotVgas_co = 0;
  float TotVref_co = 0;
  float TotVtemp_co = 0;
  
  // SO2
  const int RX3 = 4;
  const int TX3 = 5;
  SoftwareSerial SoftSerialThree(RX3,TX3);
  float TotVgas_so2 = 0;
  float TotVref_so2 = 0;
  float TotVtemp_so2 = 0;
  
  // NO2
  const int RX4 = 6;
  const int TX4 = 7;
  SoftwareSerial SoftSerialFour(RX4,TX4);
  float TotVgas_no2 = 0;
  float TotVref_no2 = 0;
  float TotVtemp_no2 = 0;
  
  // Miscellaneous
  int NumOfSamples = 0;
  
void setup(){
  // Input
  pinMode(RX1, INPUT);
  pinMode(RX2, INPUT);
  pinMode(RX3, INPUT);
  pinMode(RX4, INPUT);
  // Output
  pinMode(TX1, OUTPUT);
  pinMode(TX2, OUTPUT);
  pinMode(TX3, OUTPUT);
  pinMode(TX4, OUTPUT);
}  

void loop(){
  Serial.println("Concentrations");
  Serial.println("---------------------------------");
  
  // O3
  SoftSerialOne.begin(9600);
  float Vgas = analogRead(A0);
  float Vref = analogRead(A1);
  float Vtemp = analogRead(A2);
  TotVgas_o3 += Vgas;
  TotVref_o3 += Vref;
  TotVtemp_o3 += Vtemp;
  int Sensitivity = 31;
  int TIAGain = 499;
  float SenCalib = Sensitivity * TIAGain;
  Vgas = TotVgas_o3/NumOfSamples;
  Vref = TotVref_o3/NumOfSamples;
  Vtemp = TotVtemp_o3/NumOfSamples;
  float Concentration = (1000000 / SenCalib) * (Vgas - Vref);
  Serial.println("  Ozone: " +String(Concentration));
  SoftSerialOne.end();

  // CO
  SoftSerialTwo.begin(9600);
  Vgas = analogRead(A0);
  Vref = analogRead(A1);
  Vtemp = analogRead(A2);
  TotVgas_co += Vgas;
  TotVref_co += Vref;
  TotVtemp_co += Vtemp;
  Sensitivity = 31;
  TIAGain = 100;
  SenCalib = Sensitivity * TIAGain;
  Vgas = TotVgas_co/NumOfSamples;
  Vref = TotVref_co/NumOfSamples;
  Vtemp = TotVtemp_co/NumOfSamples;
  Concentration = (1000000 / SenCalib) * (Vgas - Vref);
  Serial.println("  Carbon Monoxide: " +String(Concentration));
  SoftSerialTwo.end();

  // SO2
  SoftSerialThree.begin(9600);
  Vgas = analogRead(A0);
  Vref = analogRead(A1);
  Vtemp = analogRead(A2);
  TotVgas_so2 += Vgas;
  TotVref_so2 += Vref;
  TotVtemp_so2 += Vtemp;
  Sensitivity = 31;
  TIAGain = 100;
  SenCalib = Sensitivity * TIAGain;
  Vgas = TotVgas_so2/NumOfSamples;
  Vref = TotVref_so2/NumOfSamples;
  Vtemp = TotVtemp_so2/NumOfSamples;
  Concentration = (1000000 / SenCalib) * (Vgas - Vref);
  Serial.println("  Sulfur Dioxide: " +String(Concentration));
  SoftSerialThree.end();

  // NO2
  SoftSerialFour.begin(9600);
  Vgas = analogRead(A0);
  Vref = analogRead(A1);
  Vtemp = analogRead(A2);
  TotVgas_no2 += Vgas;
  TotVref_no2 += Vref;
  TotVtemp_no2 += Vtemp;
  Sensitivity = 31;
  TIAGain = 100;
  SenCalib = Sensitivity * TIAGain;
  Vgas = TotVgas_no2/NumOfSamples;
  Vref = TotVref_no2/NumOfSamples;
  Vtemp = TotVtemp_no2/NumOfSamples;
  Concentration = (1000000 / SenCalib) * (Vgas - Vref);
  Serial.println("  Nitrogen Dioxide: " +String(Concentration));
  SoftSerialFour.end();
  
  Serial.println("---------------------------------");

  // Write data to file

  // Update loop and pause
  NumOfSamples++;
  delay(1000);
  
}
