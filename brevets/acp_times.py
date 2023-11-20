"""
Luke Marshall 
CS 322 Assignment 4
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

MAX_TIMINGS = { 0: 34, 200: 32, 400: 30, 600: 28 } # distance (km): max average speed in km/hr

MIN_TIMINGS =  { 0: 15, 600: 11.428 } # distance (km): min average speed in km/hr

TIME_LIMITS = { 200: 810, 400: 1620, 600: 2400, 1000: 4500} # total distance (km): time limit in minutes


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
   """
   Args:
      control_dist_km:  number, control distance in kilometers
      brevet_dist_km: number, nominal distance of the brevet
         in kilometers, which must be one of 200, 300, 400, 600,
         or 1000 (the only official ACP brevet distances)
      brevet_start_time:  An arrow object
   Returns:
      An arrow object indicating the control open time.
      This will be in the same time zone as the brevet start time.
   Raises:
      ValueError if the control distance is negative
   """
   start_time = arrow.get(brevet_start_time)
   total_time = 0
   # account for special cases
   if control_dist_km < 0: 
      # control distance is negative: raise error
      raise ValueError
   elif control_dist_km == 0: 
      # control distance is 0: starts at start time
      return start_time
   if control_dist_km > brevet_dist_km: 
      # gate beyond end of race starts at same time as end distance
      control_dist_km = brevet_dist_km

   maxs = list(MAX_TIMINGS.keys()) # list of distance intervals
   start = 0
   remaining_dist = control_dist_km
   for i in range(len(maxs)):
      if maxs[i] >= control_dist_km:
         break
      else:
         start = i
   for j in range(start, -1, -1):
      # subtract off the distance interval differences, calculate the times per difference
      # then add them all together for the total offset from the start time in minutes
      if remaining_dist == 0:
         break
      diff = remaining_dist - maxs[j]
      total_time += (diff/MAX_TIMINGS[maxs[j]])
      remaining_dist -= diff
   total_time = round(total_time * 60)
      
   return start_time.shift(minutes=total_time)


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
   """
   Args:
      control_dist_km:  number, control distance in kilometers
         brevet_dist_km: number, nominal distance of the brevet
         in kilometers, which must be one of 200, 300, 400, 600, or 1000
         (the only official ACP brevet distances)
      brevet_start_time:  An arrow object
   Returns:
      An arrow object indicating the control close time.
      This will be in the same time zone as the brevet start time.
   Raises:
      ValueError if the control distance is negative
   """
   start_time = arrow.get(brevet_start_time)
   total_time = 0
   # account for special cases
   if control_dist_km < 0: 
      # control distance is negative: raise error
      raise ValueError
   if control_dist_km == 0: 
      # control distance is 0: closes 1 hr after start by convention
      return start_time.shift(minutes=60)
   elif control_dist_km <= 60: 
      # special timing for gate closure when gate within 60km of start
      total_time = round(control_dist_km/20 * 60 + 60)
      return start_time.shift(minutes=total_time)
   if control_dist_km >= brevet_dist_km: 
      # gate beyond end of race closes at end of race
      return start_time.shift(minutes=TIME_LIMITS[brevet_dist_km])

   mins = list(MIN_TIMINGS.keys())
   start = 0
   remaining_dist = control_dist_km
   for i in range(len(mins)):
      if mins[i] >= control_dist_km:
         break
      else:
         start = i
   for j in range(start, -1, -1):
      if remaining_dist == 0:
         break
      diff = remaining_dist - mins[j]
      total_time += (diff/MIN_TIMINGS[mins[j]])
      remaining_dist -= diff
   total_time = round(total_time * 60)

   return start_time.shift(minutes=total_time)
