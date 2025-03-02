**Revised IEEE Paper Draft**

**Title: A Pygame-Based Traffic Intersection Simulation with Time-of-Day and Density-Adaptive Signal Control**

**Abstract:** This paper presents a traffic intersection simulation developed using Python and the Pygame library. The simulation models traffic flow and signal control, with a focus on adapting signal timings based on time-of-day traffic density and simulated real-time vehicle detection. The system simulates the use of object detection (e.g., YOLO) to count vehicles and, in future iterations, interpret directional indicators. This simulation provides an educational and experimental platform for evaluating the impact of dynamic signal control strategies in response to varying traffic patterns. The paper discusses the simulation's design, implementation, and potential for future expansion with real-world data integration.

**Keywords:** Traffic Simulation, Adaptive Traffic Control, Time-of-Day Traffic, Object Detection Simulation, Pygame, Python

**I. Introduction**

Urban traffic congestion is a significant problem, leading to increased travel times, fuel consumption, and air pollution. Traditional fixed-time traffic signal control systems often fail to adapt to changing traffic patterns, resulting in inefficiencies, particularly during off-peak hours or periods of sudden traffic fluctuations. To address these limitations, adaptive traffic signal control systems have emerged as a promising solution. This paper presents a traffic intersection simulation designed to explore and visualize the principles of time-of-day and density-adaptive traffic signal control.

This simulation utilizes the Pygame library to create a visually intuitive environment for experimenting with different signal timing strategies. A key feature is the incorporation of time-varying traffic density, modeled to reflect typical daily traffic patterns. Furthermore, the simulation mimics the functionality of real-time object detection systems (such as YOLO) to estimate vehicle counts, providing a data source for dynamic signal adjustments. While the current implementation uses synthetic data, the architecture is designed to accommodate real-world traffic data in future iterations. The overarching goal of this simulation is to provide an educational and experimental platform for understanding and evaluating the impact of adaptive traffic control strategies.

The contributions of this simulation include:

*   A visually accessible and modifiable Pygame-based traffic simulation.
*   An implementation of time-of-day traffic density modeling for realistic traffic flow simulation, incorporating morning and evening peak traffic periods.
*   A framework for simulating object detection and integrating vehicle count data into signal control logic for density-adaptive signal timing.

This paper is structured as follows: Section II discusses related work in traffic simulation and adaptive signal control. Section III details the methodology and system design, including the time-varying traffic density model and adaptive signal control algorithm. Section IV presents implementation details, highlighting the use of Pygame features. Section V presents preliminary results and discussion (to be completed with data collection). Finally, Section VI concludes the paper and outlines potential future work.


**II. Related Work**

Several traffic simulation tools exist, each with its own strengths and weaknesses. SUMO (Simulation of Urban Mobility) is a widely used open-source traffic simulation suite that provides detailed microscopic traffic modeling capabilities [1]. SUMO allows for the simulation of individual vehicles with realistic driving behavior, but its complexity can make it challenging to set up and customize for specific research questions. Aimsun Next is a commercial traffic simulation software that offers a comprehensive set of tools for modeling traffic networks, including macroscopic, mesoscopic, and microscopic simulation approaches [2]. Aimsun Next is powerful but requires a paid license. Vissim is another commercial microscopic traffic simulation software commonly used for traffic planning and engineering applications [3]. Vissim provides a high level of detail in its vehicle and driver models but can be computationally intensive for large-scale simulations.

[1] Lopez, P.A.; Behrisch, M.; Bieker-Walz, L.; Erdmann, J.; Genders, W.;
Hillebrand, G.; Shapiro, D.; Stiller, C.; Wagner, P. Microscopic Traffic
Simulation using SUMO. Proceedings of the 21st IEEE International Conference on
Intelligent Transportation Systems (ITSC), Maui, Hawaii, USA, Nov. 4-7, 2018; pp. 2575-2581.

[2] Barceló, J.; Casas, J.; Ferrer, J.L. AIMSUN: Advanced Interactive Microscopic Simulator for Urban and
Network Traffic. Transportation Research Record: Journal of the Transportation Research Board, 1998, 1644, 111-120.


**III. Methodology/System Design**

The traffic intersection simulation consists of several key components: vehicle generation, traffic flow modeling, object detection simulation, and adaptive signal control.

*   **Vehicle Generation:** Vehicles are generated randomly at each of the four entry points to the intersection (right, down, left, up). The probability of a vehicle being generated in each direction is assumed to be equal (25% each) based on the randomization implemented with `dist = [25,50,75,100]` and `if(temp<dist[0]): ... elif(temp<dist[1]): ...`. The vehicle type (car, bus, truck, bike) is also randomly selected with equal probability from the `allowedVehicleTypesList`, assuming all vehicle types are enabled in the `allowedVehicleTypes` dictionary.  The inter-arrival time between vehicles is determined by the `spawn_rate` variable, which is updated dynamically based on the time of day.

*   **Traffic Flow Modeling:** Vehicles move through the intersection according to predefined speeds stored in the `speeds` dictionary (car: 2.25, bus: 1.8, truck: 1.8, bike: 2.5 pixels per frame). The simulation models lane-based traffic with two lanes per direction. Vehicles in the inner lane (lane 1 and lane 2) have a 40% probability of turning [hardcoded with `if(temp<40): will_turn = 1`] at the intersection. Turning behavior is implemented using Pygame's `pygame.transform.rotate` function, rotating the vehicle image by `rotationAngle = 3` degrees per frame until a 90-degree turn is completed. The simulation uses stopping and moving gaps (`stoppingGap = 25`, `movingGap = 25` pixels) to maintain spacing between vehicles.

*   **Object Detection Simulation:** The simulation mimics the function of real-time object detection systems (like YOLO) by virtually counting vehicles that have crossed the stop line but have not yet fully cleared the intersection. This count is incremented in the `move()` function when `self.crossed == 0` and `self.x + self.image.get_rect().width > stopLines[self.direction]` or similar conditions for other directions. This provides a simplified representation of vehicle detection.

*   **Time-Varying Traffic Density:** The simulation incorporates a time-varying traffic density model to reflect realistic daily traffic patterns. The traffic density category (`vehicle_density`) is determined using the `get_density_from_time` function. The function first checks for peak hours (7:00-9:00 AM and 5:00-6:00 PM), setting the density to "high" during these times. Outside peak hours, the density is calculated based on Gaussian functions representing morning and evening traffic peaks:

```python
  morning_peak_center = 0.3  # 7:12 AM (approx.)
  evening_peak_center = 0.7  # 5:00 PM (approx.)
  peak_width = 0.2  # Adjust the width of the peaks
  morning_density = max_density * math.exp(-((time - morning_peak_center)**2) / (2 * peak_width**2))
  evening_density = max_density * math.exp(-((time - evening_peak_center)**2) / (2 * peak_width**2))
  density = 0.7 * morning_density + 0.6 * evening_density
```

**Where:**

*   `time` is equivalent to `time_of_day` represented as a fraction of a day (0.0 to 1.0).
*   `max_density` is set to 1.0.
*   `morning_peak_center = 0.3` (approximately 7:12 AM) represents the center of the morning traffic peak.
*   `evening_peak_center = 0.7` (approximately 5:00 PM) represents the center of the evening traffic peak.
*   `peak_width = 0.2` determines the width of the Gaussian distribution for the traffic peaks.
*   The values 0.7 and 0.6 weight the morning and evening densities to create combined peak hours.

**Finally, the density category is determined by the following thresholds:**

*   `density < 0.2`: "low"
*   `density < 0.7`: "medium"
*   `density >= 0.7`: "high"


**Adaptive Signal Control:** The adaptive signal control algorithm dynamically adjusts green light durations based on queue length, density, and a calculated green time. The `adapt_green_time` function calculates the green light duration for each signal using the following steps:

1.  **Queue Length Calculation:** The `queue_length` is calculated by counting the number of vehicles in each lane of a given direction whose front is behind the stop line. The `queue_length` is measured in number of vehicles.

2.  **Green Time Adjustment:** The initial green time is calculated using the formula:

```python
green_time = min_green + (max_green - min_green) * (queue_length / 20)
```

Where:

*   `min_green = 10` represents the minimum green light duration (in seconds).
*   `max_green = 20` represents the maximum green light duration (in seconds).
*   `queue_length / 20` scales the queue length to a range between 0 and 1 (assuming a maximum queue length of 20 vehicles). The divisor 20 implies that the system is designed to handle a maximum queue length of approximately 20 vehicles before fully extending the green light duration.

The calculated green time is then clamped to the range [10, 20] using the formula:

```python
green_time = max(min_green, min(max_green, int(green_time)))
```

This ensures that the green light duration stays within reasonable bounds, preventing excessively short or long green lights.

3.  **Final Green Time Adjustment:** The final green time calculation takes into account the density and saturation flow as given by the formula:

```python
calculated_green =  base_green + k * density_coefficient[vehicle_density] * total_green_yellow_time
```

Where:

*   `base_green = 5`: represents a base green time value.
*   `k = 0.1`: is a constant, it scales traffic density effects
*   `density_coefficient` maps the traffic flow densities ("low", "medium", "high") to numeric weight value to reflect traffic behaviour.
*   `total_green_yellow_time`: represents the total green time for current direction.


**IV. Implementation Details**

The traffic intersection simulation is implemented using Python 3.x and the Pygame library.

*   **Pygame Features:** The simulation leverages Pygame's sprite functionality (`pygame.sprite.Sprite`) to manage vehicles as individual objects. The `pygame.transform.rotate` function is used to implement vehicle turning, creating a visual rotation effect.  Pygame's `screen.blit()` function is used extensively to draw images (background, signals, vehicles) onto the screen. Sprite groups (`pygame.sprite.Group()`) simplify the management and rendering of multiple vehicles.

*   **Turning Logic:** When a vehicle in the inner lanes (lane 1 or 2) approaches the intersection, a random number between 0 and 99 is generated. If this number is less than 40, the vehicle will turn. Therefore, 40% represents the probability for a vehicle to take a turn in the lanes.

*   **Pausing Functionality:** The simulation includes a pause function that suspends the simulation without resetting it. This is implemented by setting a `paused` flag. When paused is `True`, vehicle movement and signal timing updates are halted. The `pause_start_time` variable is used to calculate the duration of the pause, which is then added to the `time_of_day` variable when the simulation is resumed, ensuring that the time-dependent traffic density model remains synchronized with the real-world time being simulated.

*   **Code Structure:** The code is structured using classes: `TrafficSignal` and `Vehicle`. The `TrafficSignal` class manages signal timings. The `Vehicle` class inherits from `pygame.sprite.Sprite` and manages vehicle properties (position, speed, turning behavior). The `Main` class initializes the simulation, manages the game loop, and handles user input. Threading is used to run the simulation and vehicle generation concurrently.

**V. Results and Discussion**

[**Placeholder:** *This section is *completely* dependent on the data you collect.*]

The simulation was run under two different traffic control scenarios:

*   **Scenario 1: Fixed-Time Signal Control:** In this scenario, each traffic signal was set to a fixed green light duration of 15 seconds.
*   **Scenario 2: Adaptive Signal Control:** In this scenario, the adaptive signal control algorithm described in Section III was enabled.

The simulation was run for [Specify simulation duration] under each scenario, and the following metrics were recorded:

*   Average vehicle delay (seconds).
*   Total vehicles crossed intersection in each direction (right, down, left, up).
*   Average queue length for each direction.

Table I summarizes the results of the simulation:

| Metric                        | Fixed-Time Signal | Adaptive Signal |
| ----------------------------- | ----------------- | --------------- |
| Average Vehicle Delay (s)     | [Insert Data]     | [Insert Data]   |
| Total Vehicles Crossed (Right) | [Insert Data]     | [Insert Data]   |
| Total Vehicles Crossed (Down)  | [Insert Data]     | [Insert Data]   |
| ...                           | ...               | ...             |

[**Analysis:** *Analyze the data. What do the results show? Did the adaptive signal outperform the fixed-time signal? By how much? Were there any unexpected results?*]

For example: "As shown in Table I, the adaptive signal control system resulted in a [XX]% reduction in average vehicle delay compared to the fixed-time signal. This improvement is likely due to [Explain the reasons for the improvement based on the adaptive control logic]. The simulation results also indicate that [Mention any other significant findings]. However, it's important to note that these results are based on a simplified simulation model and may not directly translate to real-world traffic conditions."

**VI. Conclusion and Future Work**

This paper presented a Pygame-based traffic intersection simulation that incorporates time-of-day traffic density and simulated object detection for adaptive signal control. The simulation provides a valuable educational tool for visualizing traffic flow and experimenting with dynamic signal timing strategies.  The simulation is designed to be extensible, allowing for the integration of more sophisticated traffic models and real-world data. The incorporation of time-varying density and simulated object detection provides a more realistic and responsive simulation environment.

Future work will focus on:

*   Integrating real-world traffic data to improve the accuracy of the traffic density model and calibrate the simulation parameters.
*   Developing a more sophisticated object detection simulation that can detect vehicle types and turning intentions with higher accuracy.
*   Implementing a graphical user interface (GUI) for easier configuration and control of the simulation, allowing users to adjust parameters such as vehicle speeds, traffic densities, and signal timing parameters.
*   Exploring different adaptive signal control algorithms, including reinforcement learning-based approaches.
*   Collecting more detailed performance data (e.g., fuel consumption, emissions) to provide a more comprehensive evaluation of the adaptive control strategy's impact.


