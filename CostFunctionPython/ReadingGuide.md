# Cost Function Trials

For calculating the weights and how the cost function should look, I hard coded a bunch of stations onto a grid with the dimensions 400x400 km. The stations each got a randomly generated queue size and price for charging the EV assigned to them.

Then an EV is spawned randomly within the grid as well, with a randomly assigned destination point. First the EV checks whether it can reach its destination without charging. If not, it checks which stations it can reach in order to charge. From there we use the cost function to determine which station is the best.

The testing of the cost function included making a bunch of not-so-thought-out mathematical equations for each cost. 

**Urgency Formulae**
U1: SoC * 100
U2: SoC² * 100
U3: 0.5 * SoC * 100
U4: SoC² + 100 * SoC
U5: SoC⁻⁰·⁵ + SoC
U6: (1 - SoC) * 100
U7: x * (SoC*100)²

**Price Formulae**
P1: ((max - min) / price) * 100
P2: -(avg - price)
P3: price - min + (range / 2)
P4: (avg - price)²
P5: (price / avg) * 100
P6: max(0, price - avg)

**Path Formulae**
D1: extraSeconds
D2: (total / orig) * 100
D3: log(total / orig) * 100
D4: (detourKm / origKm) * 100
D5: detourMin² / origMin
D6: max(0, detourMin - 5) * 60

**Queue Formulae**
Q1: queue²
Q2: queue
Q3: queue³
Q4: (queue / max) * 100
Q5: 0 if empty else queue + 10

... and then all possible combinations of all variants for the cost function were applied to calculate the lowest cost station, that would then be the decision for an EV. Then, all the individual costs, the cost function itself with the total cost, and the winning station were saved and logged to a txt file (Results.txt).

Then, the elimination process would begin. Based on each station's queue size, price and path deviation, derived from looking at the visualisation of the grid (smartev_grid.png), I would choose which station SHOULD win. Then I would go into the logs and look at which cost function combinations would result in a different station, other than the intended winning one, and eliminate variants that might have been the deciding factor for why a different station won. I saved some of these reasonings (image, logs, and seed included in the name) in the reasonsForRemovals folder, although you will have to read through it yourself to see if you agree with the decisioning. Other conclusions came from looking at the mathematic formulas, and seeing if they even made sense to have in the first place. For example, the weight of queue should not just be equals to queuesize, as it does not punish larger queues aggressively enough.

After a couple of iterations I landed on a cost function that consistently across many different seeds always picked the "right" station.

OBS: The U7 urgency cost had x as some variable that I wanted to fine tune later. After plotting the function into Geogebra, I played around with this value and finally landed on 0.02. The curve for this can be found in urgencyValueCurve.png, with the EVs SoC along the x-axis, and the cost value along the y-axis.
I think the function could have been ((SoC * 100)-20)² to get roughly the same result as well, but I digress.

## Cost function = U7 + P2 + D1 + Q3

From here, I wanted to test some weights between 0 and 1, applied to the cost functions costs, to see if this could change it's decision. The code for this can be found in weight_calculation, and the logs in weights-decision-logs.
Initially I did pretty big jumps between weights (0.2 between each), and then later refined the gap between weights for each cost. At first the EV kept picking the same station always, but then I finally hit one where the decision was split, and luckily (if you will) it picked the incorrect station a majority of the time, allowing for quicker narrowing.
The visualisation for these are saved to weight_chart.png. The logs were then saved to a bar chart diagram to visualise for myself what kind of effect they had.

Eventually I landed on the following weights:

- Urgency (U) = 0.5 => it did not have much of an influence on an EVs decision)
- Price (P) = 0.4 => Had a big influence when prices fluctuated and could single handedly decide where an EV should drive to. Was turned down a lot, so that it did flip the decision as often.
- Path Deviation (D) = 0.8 => had a lot of influence on where an EV would drive to which we wanted, but it was dominating a bit too much. Slightly tuned down.
- QueueSize (Q) = 1.0 => The most influential of the costs, has to aggressively discourage stations with large queues (and in turn wait time). 

The weights will serve as a baseline and further tuned in the SmartEV project, hence why even further refining and optimizing has been ommitted from these trials.