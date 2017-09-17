
Project 6: Stroop Effect
============
_______

# Background Information
> In a Stroop task, participants are presented with a list of words, with each word displayed in a color of ink. The participant’s task is to say out loud the color of the ink in which the word is printed. The task has two conditions: a congruent words condition, and an incongruent words condition. In the congruent words condition, the words being displayed are color words whose names match the colors in which they are printed: for example <span style="color:red">RED</span>, <span style="color:blue">BLUE</span>. In the incongruent words condition, the words displayed are color words whose names do not match the colors in which they are printed: for example <span style="color:green">PURPLE</span>, <span style="color:purple">ORANGE</span>. In each case, we measure the time it takes to name the ink colors in equally-sized lists. Each participant will go through and record a time from each condition.


# Loading Data

> Data set is retrieved from [this source](https://drive.google.com/file/d/0B9Yf01UaIbUgQXpYb2NhZ29yX1U/view).


```R
library(ggplot2)
library(repr) # resize plot
library(gridExtra) # grid for plots
library(GGally) # ggpairs - multivariate summary
```


```R
# Load the Data
se <- read.csv("stroopdata.csv")
head(se)
```


<table>
<thead><tr><th scope=col>Congruent</th><th scope=col>Incongruent</th></tr></thead>
<tbody>
	<tr><td>12.079</td><td>19.278</td></tr>
	<tr><td>16.791</td><td>18.741</td></tr>
	<tr><td> 9.564</td><td>21.214</td></tr>
	<tr><td> 8.630</td><td>15.687</td></tr>
	<tr><td>14.669</td><td>22.803</td></tr>
	<tr><td>12.238</td><td>20.878</td></tr>
</tbody>
</table>




```R
dim(se)
```


<ol class=list-inline>
	<li>24</li>
	<li>2</li>
</ol>




```R
str(se)
```

    'data.frame':	24 obs. of  2 variables:
     $ Congruent  : num  12.08 16.79 9.56 8.63 14.67 ...
     $ Incongruent: num  19.3 18.7 21.2 15.7 22.8 ...
    

# Investigation

As a general note, be sure to keep a record of any resources that you use or refer to in the creation of your project. You will need to report your sources as part of the project submission.

## 1. What is our independent variable? What is our dependent variable?

> **Independent variable** or the variable changed here for the experiment is the <u>text of colors/ink</u>.  

> **Dependent variable** or the variable which is observed is the <u>duration in which participant names all ink colors.</u>.  

## 2. What is an appropriate set of hypotheses for this task? What kind of statistical test do you expect to perform? Justify your choices.

> <p class="c2"><span>Now it’s your chance to try out the Stroop task for yourself. Go to </span><span class="c7"><a class="c8" href="https://www.google.com/url?q=https://faculty.washington.edu/chudler/java/ready.html&amp;sa=D&amp;ust=1505688389258000&amp;usg=AFQjCNGyoQJYdsm_R0nn3SJE1TUb-wWtbw">this link</a></span><span>, which has a Java-based applet for performing the Stroop task. Record the times that you received on the task (you do not need to submit your times to the site.) Now, download </span><span class="c7"><a class="c8" href="https://www.google.com/url?q=https://drive.google.com/file/d/0B9Yf01UaIbUgQXpYb2NhZ29yX1U/view?usp%3Dsharing&amp;sa=D&amp;ust=1505688389259000&amp;usg=AFQjCNHUSBUafLP3-4LLBae2NIy8gRkS1Q">this dataset</a></span><span class="c6">&nbsp;which contains results from a number of participants in the task. Each row of the dataset contains the performance for one participant, with the first number their results on the congruent task and the second number their performance on the incongruent task.</span></p>

**My results:**

**Congruent** --> 13.10s

**Incongruent** --> 22.57s
______

**Null Hypothesis:**
* H<sub>0</sub> --> Duration in which paticipant names ink color does not change when color/ink text is changed.

**Alternate Hypothesis:**
* H<sub>A</sub> --> Duration in which participant names in color increases significantly.

## 3. Report some descriptive statistics regarding this dataset. Include at least one measure of central tendency and at least one measure of variability.


```R
summary(se$Congruent)
```


       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
       8.63   11.90   14.36   14.05   16.20   22.33 



```R
summary(se$Incongruent)
```


       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
      15.69   18.72   21.02   22.02   24.05   35.26 



```R
sd(se$Congruent)
```


3.5593579576452



```R
sd(se$Incongruent)
```


4.79705712246914


**Standart Deviation:**

**Congruent** --> 3.56

**Incongruent** --> 4.80
______

## 4. Provide one or two visualizations that show the distribution of the sample data. Write one or two sentences noting what you observe about the plot or plots.


```R
options(repr.plot.width=8, repr.plot.height=4)
g1 <- ggplot(aes(x=Congruent), data=se) + geom_histogram(bins=10)
g2 <- ggplot(aes(x=Incongruent), data=se) + geom_histogram(bins=10)
grid.arrange(g1,g2,ncol=2)
```


![png](output_22_0.png)


> Both graphs seem to have a normal distribution with a few outliers at higher durations. For **Congruent** distribution, mean normal distribution is around 14, while this value is around 22 for **Incongruent** distribution.


## 5. Now, perform the statistical test and report your results. What is your confidence level and your critical statistic value? Do you reject the null hypothesis or fail to reject it? Come to a conclusion in terms of the experiment task. Did the results match up with your expectations?


```R
se$diff <- (se$Congruent - se$Incongruent)
```

I would like to set my critical value alpha at 0.05

Degrees of freedom = (24 -1) + (24 -1) = 46

> Since our alternate hypothesis indicates that the duration will increase, we can apply one tailed test at positive direction.

t<sub>critical</sub> = 2.678


```R
sd(se$diff)
```


4.86482691035905


S<sub>D</sub> = 4.86


```R
t_statistic = (22.02 - 14.05)/(4.86/sqrt(25))
t_statistic
```


8.19958847736625


t<sub>statistic</sub> = 8.20

t<sub>statistic</sub> = 8.20 is much larger than t<sub>critical</sub> = 2.678. Therefore, we can conclude that our <u>**Null Hypothesis is wrong**</u> ,and our <u>**Alternate Hypothesis is correct**</u>.

This means that changing ink text to a color name other than the ink color definitely increases the duration. 

## 6. Optional: What do you think is responsible for the effects observed? Can you think of an alternative or similar task that would result in a similar effect? Some research about the problem will be helpful for thinking about these two questions!

> I think the reason duration in which naming ink color increases is that our minds tend to read text if the text indicates a related information to the information we are looking for. In this case, we are determining color of the ink, whereas the the very text which is inked denotes a color name.
____

> A similar test is asking for number of characters in a word. In an alternate test, the words can be cahnged to the numbers.

> **For example:**

> <u>Initial test</u> --> door, school, task, medicine

> <u>Alternate test</u> --> five, seven, one, eleven
