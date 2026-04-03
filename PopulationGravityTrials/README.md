# Testing of EV's journey duration sampling on spawn

I did some testing of an EV's journey duration sampling when they are spawned. Before these trials, the EVs had a tendency to take very long journeys, often over multiple hours, since the distance scaler was only 0.8 (incentivised to take longer journeys). So in SmartEV I added an additional scaler, population scaler, and logged the journey durations into buckets of, initially, <5 mins, 5-10 mins, 10-20 mins, 20-30 mins, 30-45 mins, 45-60 mins, 60-90mins, 90-120 mins, 120-180 mins, and >180mins. The results of those can be found in data.py.

 The folder JourneyDurationsGraphs contains the visualisation of how I tweaked the scalers, with the initial (1.0, 1.0) being the baseline I wanted to improve upon. The graph here slightly lies, as these should be evenly distributed, but because the time periods get further between, it looks like there are more EV's taking longer journeys.

After I found some baseline I wanted to work with, I added a bucket for each 5 minute interval and logged those results. Those results can be found in data2.py

FineGrainedJourneyGraphs contains the visualisation for these trials, with the scalers
- distance = 1.7
- population = 0.7
Being the chosen winner. This is based off of eye measurement, and will be applied in the SmartEV repository, where further tuning and testing will applied to finally arrive on some values that we are happy with.

These tests do not consider where an EV spawns, and only about the durations. How this may affect the system is not part of these trials.