# Lego Technic Crossbow: Speed, Velocity and Trajectory

This lesson uses a Lego Technic crossbow to practice measurement, rates, unit conversion, square roots, right-triangle trigonometry and quadratic functions. Students collect real data, calculate launch speed, and compare their results to the ideal math model.

## Learning Objectives

By the end of this lesson, students can:

- Calculate **speed** from distance and time.
- Explain the difference between **speed** and **velocity**.
- Split a launch velocity into horizontal and vertical components using trigonometry.
- Predict a **trajectory** with a quadratic equation and compare it to measured data.
- Explain why real results differ from the ideal model.

## Materials

- Lego Technic crossbow and a bolt (a 13-hole beam works well)
- Phone with slow-motion video (240 fps preferred)
- Meter stick or masking tape marked every 10 cm
- Tape measure
- Stack of books or a tripod for the phone
- Calculator
- Safety glasses for everyone in the room
- Free software: [Tracker video analysis](https://physlets.org/tracker/)

<callout icon="⚠️" color="yellow_bg">
	Wear safety glasses, shoot only in one agreed direction, and keep everyone behind the firing line. Never aim at people or pets.
</callout>

## Key Concepts

### Speed vs. Velocity

*Speed* is how fast an object moves. It is a single number with units, such as 7.4 m/s.

*Velocity* is speed **plus direction**. It is described with components:

- Horizontal: **vₓ = v · cos θ**
- Vertical (at time *t*): **v_y = v · sin θ − 9.8 · t**

Here *θ* is the launch angle above horizontal, and 9.8 m/s² is the acceleration due to gravity.

### Trajectory

The *trajectory* is the path the bolt follows. With no air resistance it is a parabola:

**y = x · tan θ − (9.8 · x²) ÷ (2 · v² · cos² θ)**

### Useful Reference

The bolt is its own ruler. Lego Technic holes are spaced **8 mm** apart, so a beam is about 8 mm × (number of holes) long. A 13-hole beam is about 104 mm.

## Method 1: Slow-Motion Video

This method gives speed, velocity and the full trajectory.

1. Place the phone on a stack of books, **perpendicular** to the flight path.
2. Put a meter stick or taped marks in the background, at the same distance from the camera as the flight path.
3. Film in slow motion (240 fps if available).
4. Fire the crossbow horizontally first, then try angled shots.
5. Step through the video frame by frame and note the bolt's position at two frames.
6. Calculate speed:

**Speed = distance ÷ (frames ÷ fps)**

#### Worked Example

The bolt travels 0.5 m in 12 frames at 240 fps.

- Time = 12 ÷ 240 = 0.05 s
- Speed = 0.5 ÷ 0.05 = **10 m/s**

### Going Further With Tracker

Load the video into Tracker, set the scale using the meter stick, and click the bolt in each frame. Tracker plots x, y, vₓ and v_y, and draws the trajectory automatically.

## Method 2: Drop-and-Distance

This method needs no video. Fire the bolt **horizontally** off a table of known height *h* and measure the landing distance *d*.

1. Fall time: **t = √(2h ÷ 9.8)**
2. Launch speed: **v = d ÷ t**

#### Worked Example

Table height *h* = 0.8 m, landing distance *d* = 3 m.

- t = √(2 × 0.8 ÷ 9.8) = √0.163 ≈ 0.40 s
- v = 3 ÷ 0.40 ≈ **7.4 m/s**

### Unit Conversion Check

To convert m/s to km/h, multiply by 3.6.

7.4 m/s × 3.6 ≈ **26.6 km/h**

## Data Collection

Take at least five shots per setting and average the results, because rubber band tension varies from shot to shot.

| Shot | Band Twists | Launch Angle (°) | Table Height (m) | Distance (m) | Fall Time (s) | Speed (m/s) |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| **Average** | | | | | | |

<callout icon="💡" color="blue_bg">
	Change only one variable at a time (twists, angle or band type). Otherwise you cannot tell which change caused the difference in speed.
</callout>

## Practice Problems

1. A bolt travels 0.6 m in 15 frames of 240 fps video. What is its speed?
2. A bolt is fired horizontally from a 1.0 m table and lands 3.5 m away. What is its launch speed?
3. A bolt launches at 8 m/s at 30° above horizontal. Find vₓ, the initial v_y, the time of flight on level ground, and the range.
4. Convert your answer from Problem 2 to km/h.
5. Use the trajectory equation to predict the height *y* of a bolt at *x* = 2 m when v = 8 m/s and θ = 30°.

### Answers

1. t = 15 ÷ 240 = 0.0625 s, so speed = 0.6 ÷ 0.0625 = **9.6 m/s**
2. t = √(2 × 1.0 ÷ 9.8) ≈ 0.452 s, so v = 3.5 ÷ 0.452 ≈ **7.7 m/s**
3. vₓ = 8 cos 30° ≈ **6.93 m/s**. Initial v_y = 8 sin 30° = **4 m/s**. Time of flight = 2 × 4 ÷ 9.8 ≈ **0.82 s**. Range = 6.93 × 0.82 ≈ **5.7 m**.
4. 7.7 × 3.6 ≈ **27.7 km/h**
5. y = 2 × tan 30° − (9.8 × 4) ÷ (2 × 64 × cos² 30°) = 1.155 − 39.2 ÷ 96 ≈ 1.155 − 0.408 ≈ **0.75 m**

## Compare Theory to Reality

1. Measure the launch angle with a phone level app or protractor.
2. Plot the ideal parabola for your measured speed and angle.
3. Overlay your Tracker path on the same graph.
4. Compare the two curves.

A flat beam tumbles and has high air drag, so expect it to land **shorter** than the formula predicts. The gap between the curves shows the effect of air resistance.

### Discussion Questions

- Which angle gave the longest range? Does it match the ideal 45°?
- How did the number of band twists change launch speed? Is the relationship linear?
- Why does the real bolt land short of the parabola?
- How would the result change with a lighter or more streamlined bolt?

## Extension Ideas

- Graph launch speed against band twists and fit a line.
- Test angles of 15°, 30°, 45° and 60° and graph range against angle.
- Redesign the bolt to reduce drag and re-run the comparison.

---

Last Updated: October 2026
