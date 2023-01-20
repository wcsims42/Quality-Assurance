"""
In this example, simple time series data is used to demonstrate basic functions
in pecos.  
* Data is loaded from a CSV file which contains four columns of values that 
  are expected to follow linear, random, and sine models.
* A translation dictionary is defined to map and group the raw data into 
  common names for analysis
* A time filter is established to screen out data between 6 AM and 8 PM
* The data is loaded into a pecos PerformanceMonitoring object and a series of 
  quality control tests are run, including range tests and increment tests 
* The results are printed to CSV and HTML reports

* Only edit filenames and values in specified codeblocks (Codeblocks 1-8) *
"""
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import numpy as np
import pecos

# Initialize logger
pecos.logger.initialize()

# Create a Pecos PerformanceMonitoring data object
pm = pecos.monitoring.PerformanceMonitoring()

# * Code Block 1 *
# Populate the object with a DataFrame and translation dictionary
data_file = 'Updated_TrialSet_1.csv'
df = pd.read_csv(data_file, index_col=0, parse_dates=True)
pm.add_dataframe(df)

# * Code Block 2 *
# pm.add_translation_dictionary() groups same types of sensors (Avoids setting up checks for each sensor.)
# * If any Heat Flux or Temperature Sensors are added or removed change below. *
pm.add_translation_dictionary({'Heat Flux': ['HF1 - Unshaded (W/m2)','HF2 - Shaded (W/m2)','HF3 - Front Panel (W/m2)','HF4 - Back Panel (W/m2)','HF5 - Structure (W/m2)']}) # group heat fluxes
pm.add_translation_dictionary({'Temp': ['T1 - Unshaded (degC)','T2 - Shaded (degC)','T3 - Front Panel (degC)','T4 - Back Panel (degC)','T5 - Structure (degC)','Air Temperature (degC)']}) # group temperatures

# * Code Block 3 *
# Specify Timespan of Interest below
st = 6 # Start Time
et = 20 # End Time

# * Code Block 4 *
# Check the expected frequency of the timestamp
pm.check_timestamp(60)
 
# Generate a time filter to exclude data points early and late in the day
clock_time = pecos.utils.datetime_to_clocktime(pm.data.index)
time_filter = pd.Series((clock_time > st*3600) & (clock_time < et*3600), 
                        index=pm.data.index)
pm.add_time_filter(time_filter)

# * Line of Interest: Missing Data Filter *
# Check for missing data
pm.check_missing()

# Line of Interest: Corrupt Data Filter *        
# Check for corrupt data values
pm.check_corrupt([-999]) 

# * Code Block 5 *
# Check data for expected ranges
pm.check_range([-150, 150], 'Heat Flux')
pm.check_range([0, 50], 'Temp')
pm.check_range([0, 1300], 'Pyranometer (W/m2)')
pm.check_range([0, 360], 'Wind Direction (Degrees)')
pm.check_range([0, 30], 'Wind Speed (m/s)')

# * Code Block 6 *
# Check for stagnant data within a 1 hour moving window
pm.check_delta([0.0001, None], 3600, 'Heat Flux') 
pm.check_delta([0.0001, None], 3600, 'Temp') 
pm.check_delta([0.0001, None], 3600, 'Pyranometer (W/m2)')
pm.check_delta([0.0001, None], 3600, 'Wind Direction (Degrees)') 
pm.check_delta([0.0001, None], 3600, 'Wind Speed (m/s)') 

# * Code Block 7 *   
# Check for abrupt changes between consecutive time steps
# pm.check_increment([None, 50], 'Heat Flux') # Do we need this?
pm.check_increment([None, 3], 'Temp')
pm.check_increment([None, 100], 'Pyranometer (W/m2)')
pm.check_increment([None, 360], 'Wind Direction (Degrees)')
pm.check_increment([None, 25], 'Wind Speed (m/s)')

# * Code Block 8 *
# Compute the quality control index for HF1-HF5, T1-T5, Pyranometer, Wind Direction, and Wind Speed
mask = pm.mask[['HF1 - Unshaded (W/m2)','HF2 - Shaded (W/m2)','HF3 - Front Panel (W/m2)','HF4 - Back Panel (W/m2)','HF5 - Structure (W/m2)','T1 - Unshaded (degC)','T2 - Shaded (degC)','T3 - Front Panel (degC)','T4 - Back Panel (degC)','T5 - Structure (degC)','Pyranometer (W/m2)','Wind Direction (Degrees)','Wind Speed (m/s)','Air Temperature (degC)']]
QCI = pecos.metrics.qci(mask, pm.tfilter)

# Generate graphics
test_results_graphics = pecos.graphics.plot_test_results(pm.data, pm.test_results, pm.tfilter)
df.plot(ylim=[-1.5,1.5], figsize=(7.0,3.5))
plt.savefig('custom.png', format='png', dpi=500)

# Write test results and report files
pecos.io.write_test_results(pm.test_results)
pecos.io.write_monitoring_report(pm.data, pm.test_results, test_results_graphics, 
                                 ['custom.png'], QCI)
                                 
