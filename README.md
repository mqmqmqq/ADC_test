# ADC_test
test ADC with digital discovery

---
## test
### To start
* 3.9 ≤ python ≤ 3.11
* pip install -r requirements.txt
* The specific description and code for the power supply board is at the following address:
https://github.com/Sirius-RX/SPDev/blob/main/SPSMU/

---
### test_lib
- FFT_try
  - fft_test()
    - used to realize FFT
  - ifft_res()
    - Used to extract the residual after removing the main input frequency
- Fmin_search
  - optimiaze_sndr()
    - Used to optimize weight
- voltage_initial
  - v_initial()
    - Used to initialize the power supply board
- SGS100A_initial
  - open_and_set()
    - Used to initialize and set initial inputs
  - set_frequency()
    - Used to set the frequency
  - set_amplitude()
    - Used to set the amplitude
  - error_find()
    - Used to view all current errors
  - close()
    - Shutdown Outputs
- discovery_assit
  - led_brightness()
    - Used to control the brightness of the led on the digital discovery
  - supply_set()
    - Setting the voltage of the voltage channel

---
### Other codes
- SNDR_fminsearch
  - One FFT with fminsearch
- SNDRvsInput
  - SNDR change at scanning input
- SNDRvsVoltage
  - SNDR change at scanning volatge
- SPSmu_find
  - List all devices that can be connected
- max_input_find
  - Find the input at full swing output
- realtime_SNDR_8bit
  - An example of an 8bit real-time SNDR
- 2discovery_realtime_SNDR
  - Collect data with two discoveries
  - To do: test simultaneous triggering



